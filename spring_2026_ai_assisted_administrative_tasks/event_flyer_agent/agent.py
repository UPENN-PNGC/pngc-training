#!/usr/bin/env python3
"""
Event Flyer Agent - Workflow Overview

This agent automates the process of extracting event information from flyers and
creating calendar entries. It demonstrates key considerations in automating a real-world task:

WORKFLOW STEPS:

1. FILE MONITORING
   - Watch a folder for new event flyers (PDFs or images)
   - Detect file creation and wait for file to fully write before processing
   - This handles the race condition of incomplete uploads

2. TEXT EXTRACTION
   - PDF: Use PyMuPDF to extract embedded text
   - Images: Use EasyOCR (optical character recognition) to extract text from images
   - Clean up excessive whitespace in OCR output (common in poor-quality scans)

3. LLM-BASED INFORMATION EXTRACTION
   - Send extracted text to an LLM (OpenAI gpt-4o-mini or Ollama)
   - Ask LLM to parse unstructured flyer text into structured JSON fields:
     * Event title, date, start/end times, timezone
     * Physical venue vs. virtual meeting link (handle hybrid events)
     * Description and other details
   - Fallback to null values for missing information (don't guess)

4. TIMEZONE NORMALIZATION
   - Convert timezone abbreviations (PT, EST, etc.) to IANA timezone names
   - Critical for Google Calendar API compatibility and correct time handling
   - Preserve original event timezone while respecting user's calendar preferences

5. HYBRID EVENT HANDLING
   - If event has both physical venue and meeting link:
     * Set calendar location to venue (primary meeting place)
     * Append meeting link to description (for virtual attendees)
   - If virtual only: use meeting link as location
   - If in-person only: use venue as location

6. CALENDAR EVENT CREATION
   - Create event in Google Calendar with proper timezone context
   - Include extracted details (title, description, location, speaker info)
   - Handle authentication and calendar selection

7. DATA PERSISTENCE
   - Save extracted event data as JSON for auditing and error recovery
   - Move processed file to 'processed' folder to prevent re-processing

KEY AUTOMATION CONSIDERATIONS:
- Race condition handling: Files may not be fully written when detected
- Text quality: OCR can be noisy; LLM helps parse messy input
- Field disambiguation: Venue vs. meeting link requires explicit prompting
- Timezone complexity: Multiple representations (abbreviations, IANA names, UTC)
- Fallback strategies: Graceful degradation when data is missing
- Dual LLM support: Local (Ollama) vs. cloud (OpenAI) for cost/privacy tradeoffs
"""
import json
import time
import argparse
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import fitz  # pymupdf
import easyocr
from dateutil import parser as dateparser

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

WATCH_DIR = Path("event_dropbox")
PROCESSED_DIR = Path("processed")
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Initialize OCR reader once (CPU only, no GPU)
ocr_reader = easyocr.Reader(["en"], gpu=False)

# Global variables for LLM backend (set based on CLI arg)
llm_backend = None
openai_client = None
ollama_model = "tinyllama"


# ---------- LLM INITIALIZATION ----------
def init_llm_backend(backend, openai_api_key=None):
    """Initialize the LLM backend (OpenAI or Ollama)."""
    global llm_backend, openai_client

    llm_backend = backend

    if backend == "openai":
        from openai import OpenAI

        openai_client = OpenAI(api_key=openai_api_key)
        print("LLM Backend: OpenAI (gpt-4o-mini)")
    elif backend == "ollama":
        import ollama

        print(f"LLM Backend: Ollama ({ollama_model})")
    else:
        raise ValueError(f"Unknown backend: {backend}")


# ---------- DOCUMENT TEXT (PDF OR IMAGE) ----------
def read_document(path):
    """Extract text from PDF or image file."""
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        # Extract text from PDF
        text = ""
        doc = fitz.open(path)
        for page in doc:
            text += page.get_text()
        return text
    elif suffix in {".jpg", ".jpeg", ".png", ".tiff", ".bmp", ".gif"}:
        # Extract text from image using OCR
        results = ocr_reader.readtext(str(path))
        # Join lines and clean up excessive newlines
        text = "\n".join([line[1] for line in results])
        # Replace multiple newlines with single newline
        text = "\n".join([l.strip() for l in text.split("\n") if l.strip()])
        return text
    else:
        raise ValueError(
            f"Unsupported file type: {suffix}. "
            "Supported: .pdf, .jpg, .png, .tiff, .bmp, .gif"
        )


# ---------- LLM PARSE ----------


# ---------- LLM PARSE ----------
def extract_event(text):
    """Extract event details from text using the configured LLM backend."""
    prompt = f"""Extract event info from this flyer. Return ONLY valid JSON, no comments, no explanations.

{text}

JSON:
{{
  "title": "event title",
  "date": "YYYY-MM-DD",
  "start_time": "H:MM AM/PM",
  "end_time": "H:MM AM/PM",
  "timezone": "timezone or abbreviation",
  "venue": "physical location or null",
  "meeting_link": "Zoom/Teams/etc URL or null",
  "description": "brief description"
}}

Rules:
- Return ONLY the JSON object, nothing else
- No comments, no // or /* */ 
- Every field must have a value (use null if missing, not "null" string)
- Every field must be followed by a comma except the last field
- Do not guess. Extract actual URLs for meeting links."""

    if llm_backend == "openai":
        resp = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        content = resp.choices[0].message.content
    elif llm_backend == "ollama":
        import ollama

        response = ollama.chat(
            model=ollama_model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0},
        )
        content = response["message"]["content"]

    # Clean up response
    content = content.strip()
    if not content:
        raise ValueError("LLM returned empty response")

    try:
        result = json.loads(content)
        return result
    except json.JSONDecodeError as e:
        # If JSON parsing fails, raise error with details
        # TODO: attempt to fix, maybe w/LLM
        raise ValueError(
            f"Failed to parse JSON from LLM response: {e}\nResponse was:\n{content}"
        )


# ---------- GOOGLE AUTH ----------
def get_calendar_service():
    """Authenticate with Google Calendar API."""
    creds = None
    token = Path("token.json")

    if token.exists():
        creds = Credentials.from_authorized_user_file(token, SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        token.write_text(creds.to_json())

    return build("calendar", "v3", credentials=creds)


# Initialize calendar service
service = get_calendar_service()


# Get calendar timezone and ID from credentials
def get_calendar_config():
    """Load calendar ID and timezone from credentials.json."""
    with open("credentials.json") as f:
        creds_data = json.load(f)
        installed = creds_data.get("installed", {})
        calendar_id = installed.get("calendar_id", "primary")
        timezone = installed.get("timezone", None)

    # If timezone not in credentials, get it from Google Calendar settings
    if not timezone:
        try:
            cal_settings = service.calendarList().get(calendarId=calendar_id).execute()
            timezone = cal_settings.get("timeZone", "UTC")
        except Exception:
            timezone = "UTC"

    return calendar_id, timezone


calendar_id, calendar_timezone = get_calendar_config()


# ---------- TIMEZONE MAPPING ----------
def normalize_timezone(tz_str):
    """Convert timezone abbreviation or name to IANA timezone."""
    if not tz_str:
        return calendar_timezone

    # Mapping of common abbreviations to IANA timezones
    tz_map = {
        "PT": "America/Los_Angeles",
        "PST": "America/Los_Angeles",
        "PDT": "America/Los_Angeles",
        "MT": "America/Denver",
        "MST": "America/Denver",
        "MDT": "America/Denver",
        "CT": "America/Chicago",
        "CST": "America/Chicago",
        "CDT": "America/Chicago",
        "ET": "America/New_York",
        "EST": "America/New_York",
        "EDT": "America/New_York",
        "GMT": "UTC",
        "UTC": "UTC",
    }

    tz_upper = tz_str.upper().strip()
    return tz_map.get(tz_upper, tz_str)


def create_event(data):
    """Create a calendar event from extraed event data."""
    from datetime import datetime
    from zoneinfo import ZoneInfo

    # Validate required fields
    if not all([data.get("date"), data.get("start_time"), data.get("end_time")]):
        raise ValueError("Missing required fields: date, start_time, end_time")

    # Build title and description
    title = data.get("title") or data.get("speaker") or "Untitled Event"

    description_parts = [
        f"Speaker: {data['speaker']}" if data.get("speaker") else None,
        f"Affiliation: {data['affiliation']}" if data.get("affiliation") else None,
        data.get("description"),
    ]

    # Location: prefer venue, fall back to meeting_link
    location = data.get("venue") or data.get("meeting_link")

    # Hybrid: append meeting link to description if both exist
    if data.get("venue") and data.get("meeting_link"):
        description_parts.append(f"Meeting link: {data['meeting_link']}")

    description = "\n".join(filter(None, description_parts))

    # Parse times in event timezone, convert to calendar timezone
    event_tz = data.get("timezone") or calendar_timezone
    event_tz = normalize_timezone(event_tz)  # Convert abbreviations to IANA names

    try:
        tz = ZoneInfo(event_tz) if event_tz != "UTC" else ZoneInfo("UTC")
    except Exception:
        tz = ZoneInfo("UTC")
        event_tz = "UTC"

    start_str = f"{data['date']} {data['start_time']}"
    end_str = f"{data['date']} {data['end_time']}"

    start_dt = dateparser.parse(start_str).replace(tzinfo=tz)
    end_dt = dateparser.parse(end_str).replace(tzinfo=tz)

    # Convert to ISO format (Google Calendar API handles timezone conversion)
    event = {
        "summary": title,
        "location": location,
        "description": description,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": event_tz},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": event_tz},
    }

    try:
        result = service.events().insert(calendarId=calendar_id, body=event).execute()
        print(f"Created event: {title}")
        return result
    except Exception as e:
        print(f"Error creating event: {e}")
        raise


# ---------- FILE WATCHER ----------
def wait_for_file_ready(path, timeout=10, check_interval=0.5):
    """Wait for file to finish writing (stable size for ~1 second)."""
    start = time.time()
    last_size = -1
    stable_count = 0

    while time.time() - start < timeout:
        try:
            current_size = path.stat().st_size
            if current_size > 0 and current_size == last_size:
                stable_count += 1
                if stable_count >= 2:  # File size stable for ~1 second
                    return True
            else:
                stable_count = 0
            last_size = current_size
            time.sleep(check_interval)
        except FileNotFoundError:
            time.sleep(check_interval)

    return False


class Handler(FileSystemEventHandler):
    """Handles file creation events in the watch directory."""

    def on_created(self, event):
        # Accept PDF and image files
        supported_extensions = {
            ".pdf",
            ".jpg",
            ".jpeg",
            ".png",
            ".tiff",
            ".bmp",
            ".gif",
        }
        if not any(
            event.src_path.lower().endswith(ext) for ext in supported_extensions
        ):
            return

        path = Path(event.src_path)
        print("Processing:", path.name)

        # Wait for file to be fully written
        if not wait_for_file_ready(path):
            print(f"Timeout waiting for file to be ready: {path.name}")
            return

        try:
            text = read_document(path)
            event_data = extract_event(text)
            create_event(event_data)

            # Save extracted event JSON to processed folder
            json_path = PROCESSED_DIR / (path.stem + ".json")
            with open(json_path, "w") as f:
                json.dump(event_data, f, indent=2)

            path.rename(PROCESSED_DIR / path.name)
            print("Done\n")

        except Exception as e:
            print("Failed:", e)


# ---------- MAIN ----------
def run(backend="openai"):
    """Start the file watcher."""
    WATCH_DIR.mkdir(exist_ok=True)
    PROCESSED_DIR.mkdir(exist_ok=True)

    observer = Observer()
    observer.schedule(Handler(), str(WATCH_DIR), recursive=False)
    observer.start()

    print(f"Watching folder: {WATCH_DIR}")
    print(f"Using backend: {backend}")

    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Event Flyer Agent: Extract events from flyers and create calendar entries"
    )
    parser.add_argument(
        "--backend",
        choices=["openai", "ollama"],
        default="openai",
        help="LLM backend to use (default: openai)",
    )
    parser.add_argument(
        "--model",
        default="tinyllama",
        help="Ollama model name (default: llama3)",
    )
    parser.add_argument(
        "--openai-key",
        help="OpenAI API key (or use OPENAI_API_KEY environment variable)",
    )

    args = parser.parse_args()

    # Set Ollama model if specified
    if args.backend == "ollama":
        ollama_model = args.model

    # Initialize the LLM backend
    init_llm_backend(args.backend, openai_api_key=args.openai_key)

    # Run the agent
    run(backend=args.backend)
