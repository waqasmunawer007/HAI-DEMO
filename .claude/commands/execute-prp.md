# Execute BASE (Product Requirement Prompts) PRP

Implement a feature using using the PRP file.

## PRP File: $ARGUMENTS

## Execution Process

1. **Load PRP**
   - Read the specified PRP file
   - Understand all context and requirements
   - Check for any `*_requirements.md` or `*_REQUIREMENTS.md` documents to understand the context of the feature, especially if they are located in certain directories (meaning they are relevant to that directory)
   - Check the codebase in the root folder and the directories mentioned in the PRP, requirements, and legacy directories for context
   - Make sure to consider the integration with the existing codebase and the codebase in other directories (see the `*_requirements.md` or `*_REQUIREMENTS.md` documents for more details)
   - Check also if the feature is already implemented in the codebase, double-check, and only implement the feature if it is not implemented yet
   - Follow all instructions in the PRP and extend the research if needed
   - Ensure you have all needed context to implement the PRP fully
   - Do more web searches and codebase exploration as needed
   - Do not hardcode environment variables

2. **ULTRATHINK**
   - Think hard before you execute the plan. Create a comprehensive plan addressing all requirements.
   - Break down complex tasks into smaller, manageable steps using your todos tools.
   - Use the TodoWrite tool to create and track your implementation plan.
   - Identify implementation patterns from existing code to follow.

3. **Execute the plan**
   - Execute the PRP
   - Check first whether some of the code in the plan has been implemented, and avoid re-implementing them
   - Follow the plan, implement only code that has not been implemented yet
   - Do not over-engineer and do not write unnecessary code
   - If necessary, use Context7 to read the latest documentation on the packages used
   - Create .env.example to describe all environment variables needed

4. **Validate**
   - Run each validation command
   - Fix any failures
   - Re-run until all pass

5. **Complete**
   - Ensure all checklist items done
   - Run final validation suite
   - Report completion status
   - Read the PRP again to ensure you have implemented everything

6. **Reference the PRP**
   - You can always reference the PRP again if needed

Note: If validation fails, use error patterns in PRP to fix and retry.