def escape_like_pattern(value: str) -> str:
    """Escape SQL LIKE wildcards so user input is matched literally."""
    return (
        value.replace("\\", "\\\\")
        .replace("%", "\\%")
        .replace("_", "\\_")
    )
