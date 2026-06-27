from src.engine.walk_forward import chronological_windows


def test_walk_forward_window_count():
    assert len(list(chronological_windows(100, 40, 20, 20))) == 3
