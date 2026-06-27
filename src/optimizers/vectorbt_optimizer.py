from __future__ import annotations


def require_vectorbt():
    try:
        import vectorbt as vbt  # type: ignore
    except ImportError as exc:
        raise ImportError("Install optimizer dependencies with: pip install -e .[optimizer]") from exc
    return vbt
