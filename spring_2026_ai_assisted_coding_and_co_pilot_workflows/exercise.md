# Exercise and Discussion

## Goals

1. Explore how prompt engineering and AI-driven workflows can be used to create practical, reusable solutions for real-world bioinformatics tasks.

2. Gain hands-on experience with agentic tools in GitHub Copilot for automating and streamlining coding tasks in Visual Studio Code.

This exercise is designed to highlight:

- Iterative prompting
- The shift from code generation to agentic behavior
- Good vs better prompts without requiring advanced developer knowledge
- Realistic workflows used by practicing scientists and developers

## The Challenge

Validate VCF variants against a reference genome, report errors, and summarize variant types.

### Example Data Files

The `example_data` folder contains the following files:

- `annotation.gff3`: Example gene annotation file in GFF3 format.
- `cds_validation.txt`: Coding sequence validation results (validated against reference sequence).
- `genetic_code.tsv`: Genetic code table (tab-separated values).
- `reference.fasta`: Reference DNA sequence in FASTA format.
- `toy_protein.fasta`: Example protein sequence in FASTA format.

Not all these files are need for this task but are made available in case you want to continue to build on your code to do one or more of the following, more **advanced tasks**:

- Predict the effect of each variant on protein sequence (e.g., synonymous, missense, nonsense).
- Map variants to gene features (e.g., coding region, intron, UTR) using the annotation.
- Translate variant-affected coding sequences to protein using the genetic code.
- Identify variants that disrupt start/stop codons or splice sites.
- Summarize variant impacts at the gene or protein level.
- Annotate variants with gene names, transcript IDs, or protein changes.

---

## Task Prompt Guide

#### 1) Let AI do the breakdown

| Decent | Better |
|---|---|
| Break down the steps needed to validate variants in a VCF against a reference FASTA. | Decompose the VCF-vs-reference validation task into explicit, ordered steps: input parsing, coordinate handling, reference lookup, REF comparison, mismatch reporting, and variant classification. Be concrete and exhaustive. |

---

#### 2) Move straight to the code

| Decent | Better |
|---|---|
| Write code to validate a VCF against a reference FASTA and count variant types. | Using the defined steps, write a minimal, runnable implementation that reads a VCF and reference FASTA, checks REF alleles against the reference sequence, reports mismatches, and counts SNVs, insertions, and deletions. No abstractions or refactoring. |

---

#### 3) React to gaps

| Decent | Better |
|---|---|
| Review the code and fix any missing pieces or errors. | Identify concrete failures or ambiguities in the current implementation (e.g., coordinate indexing, multi-allelic sites, missing contigs). Patch only what is incorrect or incomplete; do not restructure working code. |

---

#### 4) Constrain behavior

| Decent | Better |
|---|---|
| Add checks and constraints to make the code safer. | Explicitly constrain behavior: enforce 1-based vs 0-based coordinates, define how multi-allelic ALT fields are handled, fail loudly on missing reference bases, and document assumptions in comments. |

---

#### 5) Push correctness

| Decent | Better |
|---|---|
| Can you review the code? | Do a code review of the current script. Point out fragile logic, duplicated code, or places where the implementation can be simplified. Refactor to clean it up while keeping behavior the same. |

---

#### 6) Test

| Decent | Better |
|---|---|
| How can I test this code? | Generate and run a focused set of tests covering main behaviors |

> **Note:** our goal here is to illustrate how Agentic AI tools in the IDE can help generate and run tests.  **Challenge**: how to change the prompt to indicate that you want to generate resuable (e.g., pytest) tests?

> Did your solution require `pandas`? If you are trying out Copilot Pro, try asking the Agent to do the following:

```Create a virtual env and install pandas```

---

#### 7) Refactor after success

| Decent | Better |
|---|---|
| Clean up and refactor the code. | Now that behavior is correct, refactor for clarity and reuse: extract functions, improve naming, add docstrings, and simplify control flow—without changing observable behavior. |

---

#### 8) Document

| Decent | Better |
|---|---|
| Add comments. | Add Google style docstrings to the module, class, and all public function members. Avoid commenting obvious Python. Remove any unnecessary comments indicating AI logic. |

---

#### 9) Demonstrate usage in a notebook

| Decent | Better |
|---|---|
| Add this to the notebook in the #codebase. | #editNotebook playground in the #codebase to import the refactored class, run it on the example VCF/FASTA, and display variant counts and validation results as a usage example. |

---

## Tips and Tricks for VSCode's integrated Copilot

- Use clear, specific comments or docstrings to guide Copilot’s suggestions.
- Start writing a function or class signature to prompt Copilot to complete the implementation (if code completions are enabled).
- Leverage Copilot’s context awareness by keeping related files open in your workspace.
- use [# prefixed keywords](#using--prefixed-keywords-in-copilot) to guide behavior and define contexts

### The .github/COPILOT.md File (for personal repositories)

You can guide GitHub Copilot’s behavior for your entire repository by adding a `.github/COPILOT.md` file. This markdown file contains prompt instructions, coding guidelines, or project-specific context that Copilot will use to generate more relevant code suggestions.  

**Best practices:**

- Place `.github/COPILOT.md` at the root of your repository or in the `.github` directory.
- Use clear, concise language to describe your coding standards, naming conventions, or architectural patterns.
- Include example prompts or code snippets to illustrate preferred solutions.
- Update the file as your project evolves to keep Copilot suggestions aligned with your needs.

This file helps ensure Copilot’s output is consistent with your team’s style and project requirements.

---

### Ask vs Agent Mode in Copilot

**Ask Mode**: Use this for quick, one-off code completions, explanations, or suggestions. Copilot responds to your prompt with a single answer or code snippet, similar to autocomplete or chat.

**Agent Mode**: Use this for more complex, multi-step tasks. Copilot acts as an agent, breaking down your request, planning steps, running code, making edits, and iterating until the task is complete. This mode is ideal for workflows that require automation, validation, or multiple actions.

Choose the mode that fits your workflow: Ask for fast help, Agent for end-to-end solutions.

---

### Using # Prefixed Keywords in Copilot

GitHub Copilot recognizes special # prefixed keywords in prompts and code comments to guide its behavior. Common examples include:

- `#codebase`: Reference the current project or workspace for context-aware code generation or search.
- `#test`, `#pytest`, `#unittest`: Indicate a testing context; prompt Copilot to generate, find, or focus on test code.
- start typing `#notebook`, `#jupyter` to get suggestions  to guide Copilot to generate code or markdown suitable for Jupyter or other notebook environments.
- `#cli`: Request command-line interface code or helpers.
- `#data`, `#dataset`: Indicate data loading, parsing, or manipulation tasks.
- `#doc`, `#docs`, `#documentation`: Focus Copilot on generating or improving documentation and docstrings.
- `#refactor`: Request code refactoring or restructuring.
- `#example`: Ask for usage examples or sample code.
- `#config`, `#settings`: Indicate configuration or settings-related code.

Use these keywords in your prompts or comments to make Copilot more effective and context-aware during code generation, testing, documentation, and workflow automation.
