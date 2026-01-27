"""
Script to update the PNGC Training course list and create course folders.
Triggered by an approved course registration issue.
"""

import os
import re
import requests
import unicodedata
import shutil


README_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "README.md"
)
COURSES_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

GITHUB_REPO = os.environ.get("GITHUB_REPOSITORY")  # e.g., 'UPENN-PNGC/pngc-training'
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/issues"

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN environment variable is not set")


def get_most_recent_registration_issue():

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    params = {
        "state": "closed",
        "labels": "registration",
        "sort": "updated",
        "direction": "desc",
        "per_page": 1,
    }
    resp = requests.get(API_URL, headers=headers, params=params)
    resp.raise_for_status()
    issues = resp.json()
    if not issues:
        raise Exception("No closed registration issues found.")
    return issues[0]


def parse_issue_body(body):
    # Extract fields from GitHub issue forms (markdown headings)
    def extract(field):
        pattern = rf"### {re.escape(field)}\\s*\\n+([^#\\n][\\s\\S]*?)(?=\\n### |\\Z)"
        match = re.search(pattern, body, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            if value.strip() in ("_No response_", "-"):
                return ""
            return value
        return ""

    title = extract("Course Title")
    year = extract("Year")
    semester = extract("Semester")
    description = extract("Course Description")
    binder = extract("Does this course require a Binder (mybinder.org) environment?")
    discussion = extract("Would you like a Discussion topic created for this course?")
    additional = extract("Additional Information")
    return {
        "title": title,
        "year": year,
        "semester": semester,
        "description": description,
        "binder": binder,
        "discussion": discussion,
        "additional": additional,
    }


def slugify(text):
    # Lowercase, remove accents, replace spaces and non-alphanum with underscores
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "_", text)
    return text.strip("_").lower()


def add_course_to_readme(course):
    with open(README_PATH, "r") as f:
        content = f.read()
    # Find the year and semester section
    year_header = f"### {course['year']}"
    semester_header = f"#### {course['semester']}"
    # If year or semester section does not exist, add it
    if year_header not in content:
        # Add year section before the --- separator (or at end if not present)
        if "\n---" in content:
            content = content.replace(
                "\n---",
                f"\n{year_header}\n\n{semester_header}\n\n- *(No courses yet)*\n\n---",
            )
        else:
            content = (
                content
                + f"\n{year_header}\n\n{semester_header}\n\n- *(No courses yet)*\n"
            )
    elif semester_header not in content:
        # Add semester section under the year header
        content = content.replace(
            year_header, f"{year_header}\n\n{semester_header}\n\n- *(No courses yet)*"
        )

    # Add bullet for the course under the semester
    pattern = rf"({re.escape(semester_header)}\n)([\s\S]*?)(?=\n#### |\n### |\n---|\Z)"
    match = re.search(pattern, content)
    if not match:
        # As a fallback, try to locate the year header and append the semester block there
        year_pattern = rf"({re.escape(year_header)}\n)([\s\S]*?)(?=\n### |\n---|\Z)"
        year_match = re.search(year_pattern, content)
        if year_match:
            insert_at = year_match.end(1)
            # Build a semester block
            semester_block = f"{semester_header}\n\n- *(No courses yet)*\n"
            content = content[:insert_at] + "\n" + semester_block + content[insert_at:]
            match = re.search(pattern, content)
    # If still not found, raise but include debug context
    if not match:
        raise Exception(
            "Semester section not found in README.md after attempted insertion"
        )
    before = match.group(1)
    section = match.group(2)
    # Remove placeholder if present
    section = re.sub(r"- \*\(No courses yet\)\*\n?", "", section)
    # Compose bullet
    bullet = f"- **{course['title']}**: {course['description']}"
    if course["binder"].lower() == "yes":
        bullet += " _(Binder)_"
    if course["additional"]:
        bullet += f" — {course['additional']}"
    section += bullet + "\n"
    # Replace section
    updated_content = content.replace(before + match.group(2), before + section)
    with open(README_PATH, "w") as f:
        f.write(updated_content)


def generate_course_readme_contents(course, folder_name):
    """
    Generate README.md content for a course folder.
    Expects course dict and target folder name
    """

    binder_choice = course["binder"].strip().lower()
    if binder_choice == "no":
        binder_section = "No Binder environment selected for this course."
    else:
        # Determine urlpath based on environment type
        if "jupyter" in binder_choice:
            urlpath = f"lab/tree"
        elif "rstudio" in binder_choice:
            urlpath = "rstudio"
        elif "shiny" in binder_choice:
            urlpath = "shiny"
        else:
            raise ValueError(f"Unrecognized Binder environment type: {binder_choice}")
        binder_section = (
            f"[![Launch Binder](https://mybinder.org/badge_logo.svg)]"
            f"(https://mybinder.org/v2/gh/{GITHUB_REPO}/HEAD?urlpath={urlpath}/{folder_name})"
        )

    discussion_section = (
        "[Go to course discussion topic](<discussion-link-placeholder>)"
    )

    readme_content = f"""# {course['title']}
    ## Description
    {course['description']}

    ---

    ## Binder
    {binder_section}

    ---

    ## Course Materials
    - *(Notebooks and code will be listed here as they are added)*

    ---

    ## Discussion
    {discussion_section}
    """
    return readme_content


def create_course_folder(course):
    folder_name = (
        f"{course['semester'].lower()}_{course['year']}_{slugify(course['title'])}"
    )
    folder_path = os.path.join(COURSES_ROOT, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    # Create placeholder README
    readme_path = os.path.join(folder_path, "README.md")
    if not os.path.exists(readme_path):
        with open(readme_path, "w") as f:
            f.write(generate_course_readme_contents(course, folder_name))

    # If Binder required, copy binder template files
    binder_choice = course["binder"].strip().lower()
    if binder_choice.lower() != "no":
        binder_path = os.path.join(folder_path, "binder")
        os.makedirs(binder_path, exist_ok=True)
        template_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            ".github",
            "binder-templates",
        )

        # copy README
        src = os.path.join(template_dir, "README.md")
        dst = os.path.join(binder_path, "README.md")
        shutil.copyfile(src, dst)

        is_python_env = "jupyter" in binder_choice.lower()
        runtime_path = os.path.join(binder_path, "runtime.txt")
        if not os.path.exists(runtime_path):
            if is_python_env:
                with open(runtime_path, "w") as f:
                    f.write("python-3.12\n")
            else:
                from datetime import date

                today = date.today().isoformat()
                with open(runtime_path, "w") as f:
                    f.write(f"r-3.6-{today}\n")


def main():
    issue = get_most_recent_registration_issue()
    course = parse_issue_body(issue["body"])
    add_course_to_readme(course)
    create_course_folder(course)


if __name__ == "__main__":
    main()
