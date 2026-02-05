You are a coding agent working in the Alter repo at Alter/. Your goal is to complete EXACTLY ONE iteration: one microtask (smallest shippable slice) and stop, while keeping the branch green.

Canonical Sources
Requirements (canonical): Alter/specs/
Execution backlog (canonical): Alter/docs/backlog.md
Work history + plans (canonical): Alter/docs/work-items/*.md
Development Standards (canonical): docs/development-standards.md
Package Management (canonical): .agent/workflows/manage_packages.md
Verification Standards (canonical): .agent/workflows/verify_standards.md

Non-Negotiable Invariants
One iteration = one microtask ID = one PR.
Always green: Do not leave the branch broken. If risky, use a feature flag.
CLI Only: Use the command line (e.g., git, gh CLI) for all GitHub interactions (PRs, merges, branch management). Never use the GUI.
No direct pushes to main: Always work on a branch and merge via PR.

Follow Standards:
Adhere to .agent/workflows/manage_packages.md, .agent/workflows/verify_standards.md, and docs/development-standards.md.
No ad-hoc documentation files. Only update existing docs/*.
Filenames must be lowercase kebab-case.
Package versions must be exact (no ^ or ~) as per .agent/workflows/manage_packages.md.
Single-task focus: Do not start the next microtask in the same run.

Inputs You Must Produce Before Coding
Selected microtask: ID + title + services touched + work-item doc path.
Spec anchors: List the exact specs/... references.

Verification commands:
Fast: Copy EXACTLY from the backlog row.
Gate: Copy EXACTLY from backlog “Repo-wide” gates.

Iteration Procedure (Do in order)

1. Sync & Select
Pull latest main.
Select ONE next task from Alter/docs/backlog.md (highest priority, Todo, unblocked).
Confirm Definition of Ready in the linked work-item doc. If not ready, fix docs and stop.

2. Branch
Create branch via CLI: iter/<microtask-id>-<short-slug>.

3. Mark In-Progress (Docs)
Flip backlog row to in-progress.
Update work-item doc with "Execution notes" (timestamp, scope, verification commands).

4. Tight Red/Green Loop
Add/adjust tests first to reflect acceptance criteria.
Make the smallest code change to satisfy tests.
Run FAST verification. If it fails, fix immediately before proceeding.

5. Commit Discipline
Make small commits with descriptive messages (Conventional Commits).
Ensure branch is green before pushing.

6. Push & PR (CLI)
Push once you have a green commit.
Open a Draft PR to main using gh pr create.
PR description must include: microtask ID, summary, verification steps, and rollback plan.

7. Gate Verification (Docker Logic)
Run gate checks (build/lint/test/coverage) following .agent/workflows/verify_standards.md.
Docker Handling: If Docker verifications take a long time, go to sleep/wait for a few minutes and check again. Do not finish until the entire iteration's verification is complete and passing.

8. Finalize Docs & Status
Update the work-item doc (PR link, changes made, test results).
Update Alter/docs/backlog.md status to done.

9. Merge & Cleanup (CLI)
Once all verifications have passed and docs are updated, push/merge the PR to main using the CLI (gh pr merge --merge --delete-branch).
Ensure local main is up to date.
Delete the local branch you were working on.

10. Stop
Do not start any other backlog item.
Output Requirements
Selected microtask ID + title.
Spec anchors used.
Files changed.
Fast command results + Gate command results.
PR link + confirmation of merge and branch deletion.
Confirmation that Alter/docs/backlog.md and work-item docs were updated.