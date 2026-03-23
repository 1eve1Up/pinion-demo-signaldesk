#!/usr/bin/env python3
"""
Plot per-commit LOC from git (not sprint merge rollups / cumulative totals).

Reads PIN-tagged commits from sprints/artifacts/*/commits/git-log.txt, then for each commit
runs ``git show --shortstat`` in --repo-root to get insertions and deletions for that
commit only.

- **LOC**: insertions (+) in that commit.
- **Net LOC**: insertions − deletions for that commit.

X-axis: chronological commits; tick labels are work unit id (PIN-###) and minutes after the
previous plotted commit.

Requires: matplotlib; git on PATH for --repo-root.

Usage:
  python sprints/plot_artifact_commits_loc.py
  python sprints/plot_artifact_commits_loc.py --artifacts-dir sprints/artifacts --output loc.png
"""

from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

PIN_RE = re.compile(r"\b(PIN-\d+)\b")
GIT_LINE_RE = re.compile(
    r"^([0-9a-f]{40})\s+(\S+)\s+(.+)$",
    re.MULTILINE,
)
REPO_ROOT_LINE_RE = re.compile(r"repo root:\s*`([^`]+)`")
INSERTIONS_RE = re.compile(r"(\d+)\s+insertions?\(\+\)")
DELETIONS_RE = re.compile(r"(\d+)\s+deletions?\(-\)")


@dataclass(frozen=True)
class CommitRow:
    sha: str
    when: datetime
    subject: str
    pin: str


def _parse_git_log(text: str) -> list[CommitRow]:
    rows: list[CommitRow] = []
    for m in GIT_LINE_RE.finditer(text):
        sha, iso, subject = m.group(1), m.group(2), m.group(3).strip()
        pin_m = PIN_RE.search(subject)
        if not pin_m:
            continue
        when = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        if when.tzinfo is None:
            when = when.replace(tzinfo=timezone.utc)
        rows.append(
            CommitRow(
                sha=sha,
                when=when.astimezone(timezone.utc),
                subject=subject,
                pin=pin_m.group(1),
            )
        )
    return rows


def _repo_root_from_artifacts(artifacts_dir: Path) -> Path | None:
    for log_path in sorted(artifacts_dir.glob("*/commits/git-log.txt")):
        text = log_path.read_text(encoding="utf-8")
        m = REPO_ROOT_LINE_RE.search(text)
        if m:
            return Path(m.group(1))
    return None


def _git_commit_insertions_deletions(repo: Path, sha: str) -> tuple[int, int]:
    """Return (insertions, deletions) for a single commit via git show --shortstat."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), "show", "--format=", "--shortstat", sha],
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired):
        return 0, 0
    if proc.returncode != 0:
        return 0, 0
    line = (proc.stdout or "").strip()
    if not line:
        return 0, 0
    ins_m = INSERTIONS_RE.search(line)
    del_m = DELETIONS_RE.search(line)
    insertions = int(ins_m.group(1)) if ins_m else 0
    deletions = int(del_m.group(1)) if del_m else 0
    return insertions, deletions


def _dedupe_commits(rows: Iterable[CommitRow]) -> list[CommitRow]:
    by_sha: dict[str, CommitRow] = {}
    for r in rows:
        by_sha[r.sha] = r
    return sorted(by_sha.values(), key=lambda r: (r.when, r.sha))


def _minutes_later(prev: datetime | None, cur: datetime) -> float | None:
    if prev is None:
        return None
    return (cur - prev).total_seconds() / 60.0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Plot per-commit LOC from git + PIN commits in sprint artifacts."
    )
    parser.add_argument(
        "--artifacts-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "artifacts",
        help="Directory containing sprint-*/commits/git-log.txt (PIN-tagged commits)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write PNG to this path (default: display interactively)",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Git repository root (default: from git-log header, else parent of sprints/)",
    )
    args = parser.parse_args()
    artifacts_dir: Path = args.artifacts_dir

    try:
        import matplotlib.pyplot as plt
    except ImportError as e:
        raise SystemExit(
            "matplotlib is required. Install with: pip install matplotlib"
        ) from e

    fallback_root = Path(__file__).resolve().parents[1]
    candidates: list[Path] = []
    if args.repo_root is not None:
        candidates.append(args.repo_root)
    hdr_root = _repo_root_from_artifacts(artifacts_dir)
    if hdr_root is not None:
        candidates.append(hdr_root)
    candidates.append(fallback_root)

    repo_root: Path | None = None
    for cand in candidates:
        r = cand.expanduser().resolve()
        if (r / ".git").is_dir() or (r / ".git").is_file():
            repo_root = r
            break
    if repo_root is None:
        raise SystemExit(
            "Could not find a git repo. Tried --repo-root, git-log 'repo root' line, and "
            f"{fallback_root}. Pass --repo-root explicitly."
        )

    all_rows: list[CommitRow] = []
    for log_path in sorted(artifacts_dir.glob("*/commits/git-log.txt")):
        all_rows.extend(_parse_git_log(log_path.read_text(encoding="utf-8")))

    commits = _dedupe_commits(all_rows)
    if not commits:
        raise SystemExit(f"No PIN-tagged commits found under {artifacts_dir}")

    labels: list[str] = []
    loc_vals: list[float] = []
    net_vals: list[float] = []
    prev_t: datetime | None = None

    for c in commits:
        insertions, deletions = _git_commit_insertions_deletions(repo_root, c.sha)
        loc_vals.append(float(insertions))
        net_vals.append(float(insertions - deletions))

        delta = _minutes_later(prev_t, c.when)
        prev_t = c.when
        if delta is None:
            time_part = "start"
        else:
            time_part = f"+{delta:.1f} min"
        labels.append(f"{c.pin}\n{time_part}")

    n = len(commits)
    x = list(range(n))
    width = 0.38
    fig, ax = plt.subplots(figsize=(max(8.0, n * 0.55), 5.5))
    ax.bar(
        [i - width / 2 for i in x],
        loc_vals,
        width,
        label="LOC (insertions)",
        color="#1565c0",
    )
    ax.bar(
        [i + width / 2 for i in x],
        net_vals,
        width,
        label="Net LOC (insertions − deletions)",
        color="#2e7d32",
    )
    ax.set_ylabel("Lines of code (this commit only)")
    ax.set_xlabel("Commit (work unit, time since previous)")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=8)
    ax.legend(loc="upper left")
    ax.set_title("Per-commit LOC vs net LOC (git shortstat)")
    ax.axhline(0, color="gray", linewidth=0.8, linestyle="--", alpha=0.7)
    fig.tight_layout()

    if args.output:
        fig.savefig(args.output, dpi=150, bbox_inches="tight")
        print(f"Wrote {args.output.resolve()}")
    else:
        plt.show()


if __name__ == "__main__":
    main()
