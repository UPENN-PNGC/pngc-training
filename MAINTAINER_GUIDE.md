# PNGC Training Maintainer Guide

## Reviewing and Approving Course Registrations (Automated Workflow)

1. **Review the submitted registration issue:**
   - Check that all required fields are completed and the course details are valid.
   - Confirm the course meets PNGC Training criteria, including description and instructor information.

2. **Approve the registration:**
   - Add the `approved` label to the issue (the `registration` label is set by the issue template).

3. **Automated PR and Notification:**
   - When an issue is approved, the `Update PNGC Training Courses` GitHub Action is triggered.
   - This action:
     - Creates a new branch and a pull request (PR) for the course.
     - Updates the branch README and creates the course folder and template files.
     - Posts a comment on the issue, tagging the submitter, with instructions for checking out the branch and adding course materials.

4. **Submitter adds materials:**
   - The course submitter adds materials to the PR branch and sets the issue label to `ready for review` when done.

5. **Automated Reviewer Notification:**
   - When the `ready for review` label is added to an approved registration issue, the `Notify Reviewers When Course PR Ready` GitHub Action is triggered.
   - This action:
     - Finds the linked PR and posts a comment tagging the repo owners for review.

6. **Review and merge:**
   - Repo owners review the PR, request changes if needed, and merge when ready.
   - Add a discussion topic for this course to the repository discussion (manual step).

## Removing a Registered Course

**Note:** Removal is done manually.  

- Branch or fork the repository.  
- Remove references to the course from the README
- Remove the dedicated course material directory in the repository in your branch/fork.  
- Submit a PR to push the code changes.
- Archive or remove associated discussion topic in the repository Discussion group.

## Notes

- For troubleshooting workflow failures, see the Actions tab and review logs for missing dependencies, permissions, or token issues.
