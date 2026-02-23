# Event Flyer Agent

## Generating Google Calendar API credentials (updated)

Google Cloud's UI changes frequently. These instructions follow the current flow (Feb 2026) and avoid UI-specific menu names that move around.

High-level steps you'll perform:

- Select or create a Google Cloud project
- Enable the Google Calendar API for that project
- Configure the OAuth consent screen (if required)
- Create an OAuth client ID (Desktop app) and download the JSON

Detailed steps:

1. Open the Google Cloud Console: [https://console.cloud.google.com/](https://console.cloud.google.com/)
2. Project selection:
   - Click the project selector at the top of the page (it shows the current project name).
   - Either select an existing project or choose the option to create a new project from the selector dialog.
   - If you create a new project, wait a moment while it initializes.

3. Enable the API:
   - Use the search box at the top of the Cloud Console and search for "Google Calendar API".
   - Click the result and press **Enable** for the selected project.

4. OAuth consent screen (only needed if prompted):
   - If this is your first time creating OAuth credentials in the project, the console may walk you through configuring an OAuth consent screen.
   - Select "External" for broad testing, or "Internal" if you are within a Google Workspace organization and that fits your use case.
   - Provide an application name and support email. You do not need to publish the app to create test credentials; adding yourself as a test user is usually sufficient.

5. Create credentials:
   - Navigate to **APIs & Services > Credentials** (or open the Credentials page from the left-hand menu after enabling the API).
   - Click **Create Credentials** and choose **OAuth client ID**.
   - For the application type pick **Desktop app** (this is the simplest option for local scripts).
   - Provide a name (e.g., "Event Flyer Agent") and create the client.
   - Download the JSON that is offered. Save it to this repository folder as `credentials.json`.

6. First-run token generation:
   - The first time you run the script it will open a browser to authorize the app. After successful authorization, a `token.json` file will be written to the same folder. Keep `token.json` private; it stores an access/refresh token.

Example `credentials.json` (template — replace with values Google provides):

```json
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": [
      "http://localhost"
    ],
    "calendar_id": "calendar-id-here"
  }
}
```

**Note on `calendar_id`:** The optional `calendar_id` field specifies which Google Calendar events are added to. If omitted, events are added to your primary (default) calendar. Calendar IDs vary by type:

- Personal Gmail calendar: your email address (e.g., `user@gmail.com`)
- Custom calendar: UUID-like ID (e.g., `abc123def456@group.calendar.google.com`)

To find your calendar's ID:

- Open Google Calendar
- Go to Settings > Calendars
- Click the calendar you want to use
- Scroll to "Calendar ID" and copy it

Troubleshooting & notes

- If you can't find the "Create Credentials" button, open the Credentials page directly:

   [https://console.cloud.google.com/apis/credentials?project=<YOUR_PROJECT_ID>](https://console.cloud.google.com/apis/credentials?project=<YOUR_PROJECT_ID>)

- Google Calendar API does not require billing to be enabled for standard read/write access for most apps.
- If you configured an OAuth consent screen with an "External" type, you may need to add test users before the consent screen allows sign-in for non-published apps.
- Keep `credentials.json` and `token.json` out of git. Add them to `.gitignore` if needed.
- If your app fails to authorize, delete `token.json` and re-run the script to restart the OAuth flow.

Security

- Never share client secret values in public repositories.
- Use a separate Google Cloud project for development/testing if possible.

## Installation

### Create virtual environment and install dependencies

```bash
# create and activate a venv
python3 -m venv .venv
source .venv/bin/activate

# install PyTorch and torchvision CPU-only (important: must be compatible versions)
pip install torch==2.3.0 torchvision==0.18.0 --index-url https://download.pytorch.org/whl/cpu

# install remaining dependencies
pip install -r requirements.txt
```

**Note:** PyTorch and torchvision are installed from the CPU-only index first with matching versions to prevent version mismatches and CUDA bindings. This keeps the installation lightweight (~500MB instead of 2GB+).

Make sure you have `credentials.json` in this folder.

## Running the agent

The unified `agent.py` supports both OpenAI and Ollama backends via command-line flags.

### OpenAI-backed agent

```bash
export OPENAI_API_KEY="sk-..."
python agent.py --backend openai
```

### Ollama-backed agent

Requirements: A running Ollama server with a compatible model installed. See the [Ollama docs](https://ollama.com/docs) for installation and model setup.

```bash
# using default model (llama3)
python agent.py --backend ollama

# or specify a different model
python agent.py --backend ollama --ollama-model neural-chat
```

### First run

On first run, the script will open a browser to complete Google OAuth and will write a `token.json` file with the calendar OAuth tokens. Keep this file private; it stores your access/refresh token.

### Notes

- Supported file types: `.pdf`, `.jpg`, `.jpeg`, `.png`, `.tiff`, `.bmp`, `.gif`
- The agent monitors `event_dropbox/` folder for new files
- Processed files are moved to `processed/` folder
- If you get errors about missing Python packages, confirm your Python interpreter and pip are from the venv (use `which python` and `which pip`)
