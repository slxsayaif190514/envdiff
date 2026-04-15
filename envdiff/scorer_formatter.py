"""Format a CompatibilityScore for terminal output."""

from __future__ import annotations

from envdiff.scorer import CompatibilityScore


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def _green(s: str) -> str:
    return f"\033[32m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _red(s: str) -> str:
    return f"\033[31m{s}\033[0m"


def _color_grade(grade: str) -> str:
    if grade == "A":
        return _green(grade)
    if grade in ("B", "C"):
        return _yellow(grade)
    return _red(grade)


def format_score(score: CompatibilityScore, file_a: str = "", file_b: str = "") -> str:
    lines: list[str] = []

    header = "Compatibility Score"
    if file_a and file_b:
        header += f": {file_a}  vs  {file_b}"
    lines.append(_bold(header))
    lines.append("-" * 40)

    grade = score.grade()
    colored_grade = _color_grade(grade)
    score_line = f"  Score : {_bold(f'{score.score:.1f}/100')}  (Grade: {colored_grade})"
    lines.append(score_line)
    lines.append(f"  Total keys   : {score.total_keys}")
    lines.append(f"  Matching     : {_green(str(score.matching_keys))}")

    missing_b_str = str(score.missing_in_b)
    missing_a_str = str(score.missing_in_a)
    mismatch_str = str(score.mismatched)

    if score.missing_in_b:
        missing_b_str = _red(missing_b_str)
    if score.missing_in_a:
        missing_a_str = _red(missing_a_str)
    if score.mismatched:
        mismatch_str = _yellow(mismatch_str)

    lines.append(f"  Missing in B : {missing_b_str}")
    lines.append(f"  Missing in A : {missing_a_str}")
    lines.append(f"  Mismatched   : {mismatch_str}")

    return "\n".join(lines)
