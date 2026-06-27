from __future__ import annotations


def require_backtrader():
    try:
        import backtrader as bt  # type: ignore
    except ImportError as exc:
        raise ImportError("Install replay dependencies with: pip install -e .[replay]") from exc
    return bt
