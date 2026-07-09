# Contributing to AquaSense

Thanks for your interest in AquaSense. This started as a capstone project,
but issues, bug reports, and pull requests are welcome.

## Getting set up

Follow the [Setup section](README.md#setup) in the README — either
`docker compose up -d` for the full stack, or the local dev instructions for
running the backend/frontend separately with hot reload.

## Making a change

1. Fork the repo and create a branch off `main`.
2. Make your change. Keep commits focused — one logical change per commit.
3. Run the relevant checks before opening a PR (see below).
4. Open a PR describing what changed and why. Link any related issue.

## Code style

- **Backend (Python)**: follow the existing style in `app/` — type hints on
  function signatures, docstrings on public functions that aren't
  self-explanatory, no bare `except`. Domain-science assumptions (fallback
  formulas, simplifications) should be documented in a comment, the same way
  the existing `services/et0.py` and `services/water_balance.py` do.
- **Frontend (TypeScript)**: match the existing component structure — typed
  props, Tailwind utility classes rather than custom CSS, API calls go
  through `src/api/`, not inline `fetch`/`axios` calls in components.

## Tests

The ET0 and water-balance calculations are the core of this project, so any
change to `app/services/et0.py` or `app/services/water_balance.py` should
come with a test using a known-good reference value (a FAO-56 worked example,
or a hand-computed value you can show your work for) — see
`backend/tests/test_et0.py` and `backend/tests/test_water_balance.py` for the
existing pattern.

Run the backend test suite before opening a PR:

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. pytest tests/ -v
```

For frontend changes, at minimum run:

```bash
cd frontend
npx tsc --noEmit
npm run build
```

## Reporting bugs / proposing features

Open a GitHub issue. For bugs, include steps to reproduce and what you
expected vs. what happened. For domain-science issues (e.g. a coefficient
that looks wrong, or a formula that doesn't match FAO-56), please cite the
source/table you're comparing against.

## Scope note

This project intentionally simplifies some things for a capstone timeline
(see "What I'd do with more time" in the README) — e.g. no persisted
irrigation event log, single-layer soil model, a daily-adapted effective
rainfall formula. PRs that address those are especially welcome, but please
open an issue first to discuss the approach before a large change.
