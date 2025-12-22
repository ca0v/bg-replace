---
agent: agent
---
You are going to generate code from a collection of implementation specifications.

First, read all the implementation specifications from the folder ./specs/implementation.

Then, generate the corresponding source code based on those specifications.

When generating the source code, label each public method with the appropriate IMP-XXXX identifier as specified in the implementation specification. For each public method, add a comment immediately above its declaration in the format: `// <module_name>/IMP-XXXX` for JavaScript or `# <module_name>/IMP-XXXX` for Python, where `<module_name>` is derived from the specification file name (e.g., for `bg-replace.impl.md`, use `bg-replace`). Do not modify the code logic; only add these reference comments. If a method already has a comment, prepend the IMP-XXXX reference to it.

Generate complete, runnable source code, including any supporting files (e.g., HTML, CSS) that are referenced in the specification or necessary for the application to function. Ensure the code matches the described functionality, algorithms, and dependencies.

Place the generated source code into the ./codegen folder, maintaining the directory structure as described in the specification (e.g., backend/static/ for frontend files).

After generation, validate the code by attempting to run or import it. If a virtual environment exists (e.g., bust_env), activate it before running Python code. Check for import errors and ensure the application starts without critical failures. If issues arise, iterate on the code generation to fix them.