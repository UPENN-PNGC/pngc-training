# PNGC Training Maintainer Guide

## Reviewing and Approving Course Registrations

1. **Review the submitted registration issue:**
   - Check that all required fields are completed and the course details are valid.
   - Confirm the course meets PNGC Training criteria, including description and instructor information.

2. **Approve the registration:**
   - Add the `approved` label to the issue.
   - Ensure the issue also has the `registration` label (set by the issue template).

3. **Close the issue:**
   - Closing an issue with both `approved` and `registration` labels will automatically trigger the workflow to add the course to the README and create the course folder.
   - If this does not occur, check the `Actions` tab to investigate why the automation may have failed.
  
4. **Create the discussion topic:**
   - Add a discussion topic for this course to the respository discussion.  Details TBD.

## Removing a Registered Course

**Note:** Removal is done manually.  

- Branch or fork the repository.  
- Remove references to the course from the README
- Remove the dedicated course material directory in the repository in your branch/fork.  
- Submit a PR to push the code changes.
- Archive or remove associated discussion topic in the repository Discussion group.
  
## Notes

- If the workflow is skipped, check that both required labels (`approved` and `registration`) are present before closing the issue.
- For troubleshooting workflow failures, see the Actions tab and review logs for missing dependencies or permissions.
