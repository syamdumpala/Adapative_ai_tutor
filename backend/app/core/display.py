"""Pure presentation helpers shared across features.

These mirror the frontend's name rules so the API can own the split the UI used
to do client-side (``initialsOf`` / ``fullName`` in the Mira codebase).
"""


def split_name(full_name: str) -> tuple[str, str]:
    """Split a display name into (first, last). Everything after the first token is 'last'."""
    parts = full_name.strip().split()
    if not parts:
        return "", ""
    return parts[0], " ".join(parts[1:])


def initials_of(full_name: str) -> str:
    """First letters of the first two whitespace tokens, uppercased (fallback 'M')."""
    parts = full_name.strip().split()
    first = parts[0][0] if parts and parts[0] else "M"
    second = parts[1][0] if len(parts) > 1 and parts[1] else ""
    return (first + second).upper()


def improvement_str(pct: int) -> str:
    """Format an improvement percentage as the signed string the UI parses (e.g. '+38%')."""
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct}%"
