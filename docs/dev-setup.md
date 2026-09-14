# Development setup

This project moved from macOS to Windows partway through. The notes below exist
so that neither machine produces a diff the other cannot read, and so the same
inputs produce the same outputs on both.

## Prerequisites

- Python as pinned in `.python-version`. Do not use a different minor version.
- [uv](https://docs.astral.sh/uv/) for dependency resolution. The committed
  `uv.lock` is what makes resolution identical across machines, so use uv rather
  than bare pip.
- git 2.30 or later.

## First run

### Windows, PowerShell

```powershell
cd "C:\Preeti\Personal projects"
git clone https://github.com/pretzelslab/ai-value-lab
cd ai-value-lab
uv sync
uv run streamlit run app.py
```

### macOS or Linux

```bash
git clone https://github.com/pretzelslab/ai-value-lab
cd ai-value-lab
uv sync
uv run streamlit run app.py
```

## Checks

```bash
uv run ruff check .
uv run pytest
```

Both must pass before a commit. CI runs the same two commands, so a green local
run and a red CI run means something differs about the environment, not the code.

## Rules that prevent cross platform pain

**Never copy a virtual environment between machines.** A `.venv` built on macOS
contains absolute paths and compiled artefacts that are meaningless on Windows.
Delete it and run `uv sync` instead. It takes seconds.

**Never copy the working folder between machines.** Clone from the remote. A
copied folder carries editor state, stale caches and line ending damage.

**Line endings are handled by `.gitattributes`**, which normalises everything to
LF in the repository. If you see a diff claiming every line of a file changed,
the file was written by a tool that ignored it. Fix the tool, do not commit the
diff. To renormalise an existing checkout once:

```bash
git add --renormalize .
git status
```

**Use `pathlib`, never string concatenation, for paths.** `Path("data") / "cases.jsonl"`
works everywhere. `"data/" + name` and `os.path.join` with hardcoded separators do
not.

**Import casing matters, and only CI will tell you.** Both macOS and Windows have
case insensitive filesystems, so `import Risk_Profiles` will work locally and fail
on Linux CI. CI is the arbiter. Do not dismiss a CI only failure as flaky.

**Pre-commit hooks are per clone.** Reinstall them after cloning on a new machine.

## Determinism

The economic model must be deterministic: same inputs, same outputs, byte for
byte, on any machine. No wall clock, no locale dependent formatting, and no
unordered iteration inside the calculation modules.

The cross platform check is the determinism check. Export an assessment as JSON
on both machines with identical inputs and diff them. If they differ, something
in the model depends on the environment and that is a defect, not a quirk.

```bash
uv run python -m ai_value_lab.export --scenario baseline --out /tmp/baseline.json
```

## Streamlit notes

`streamlit run app.py` may need to be invoked as `python -m streamlit run app.py`
on Windows if the console script is not on PATH. Using `uv run` avoids this.

Streamlit caches aggressively. If a change to the model does not appear in the
interface, clear the cache from the menu in the top right rather than assuming the
change did not apply.

## Secrets

There are no secrets required to run the economics engine. When the evaluation
adapter is added, its API key is read from the environment only. Never place a
key in `.streamlit/secrets.toml`, in a profile YAML, or in a notebook. `.env` is
gitignored and `.env.example` shows the variable names without values.

## What not to commit

- `.venv/`, `__pycache__/`, `.pytest_cache/`
- `evidence/` raw evaluation outputs, which may contain realistic case content
- Any file containing a real customer, employee or client name
