# Sprints

This folder holds sprint markdown (`sprint-*.md`), Pinion retro **artifacts** under `artifacts/`, and a small helper to chart per-commit LOC from those artifacts.

## Artifacts

After a sprint close with retro emit enabled, Pinion writes bundles such as:

- `artifacts/<sprint-id>/commits/git-log.txt` — commit hashes, timestamps, subjects
- `artifacts/<sprint-id>/metrics.json` — merge-time stats per work unit (not used by the plotter)

## Per-commit LOC chart

[`plot_artifact_commits_loc.py`](plot_artifact_commits_loc.py) reads every `artifacts/*/commits/git-log.txt`, keeps commits whose subject contains `PIN-###`, dedupes by SHA, sorts oldest → newest, then for each commit runs `git show --shortstat` in the chosen repo to plot **this commit only**:

- **LOC** — insertions `(+)`
- **Net LOC** — insertions minus deletions

**Requirements:** Python 3.11+, `git` on `PATH`, and `matplotlib` (`pip install matplotlib`).

From the **repository root** (the directory that contains `.git` and `sprints/`):

```bash
pip install matplotlib
python sprints/plot_artifact_commits_loc.py --output loc-by-commit.png
```

Useful options:

| Flag | Purpose |
| --- | --- |
| `--artifacts-dir DIR` | Default is `sprints/artifacts` next to the script. |
| `--repo-root DIR` | Git repo containing those commit SHAs. If omitted, the script tries the `repo root:` line inside the git-log files, then the parent of `sprints/` (project root). |
| `--output FILE.png` | Save the figure; omit to open an interactive window. |

If Matplotlib cannot write its config cache (e.g. some CI or sandboxes), set a writable directory:

```bash
export MPLCONFIGDIR=/tmp/mplconfig
mkdir -p "$MPLCONFIGDIR"
```
