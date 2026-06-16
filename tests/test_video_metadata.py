from __future__ import annotations

from media_agent.video.metadata import _parse_frame_rate


def test_parse_frame_rate_handles_common_fractional_rates() -> None:
    assert _parse_frame_rate("24/1") == 24.0
    assert _parse_frame_rate("30000/1001") == 29.97


def test_parse_frame_rate_handles_missing_or_invalid_values() -> None:
    assert _parse_frame_rate(None) is None
    assert _parse_frame_rate("") is None
    assert _parse_frame_rate("0/0") is None
    assert _parse_frame_rate("not-a-rate") is None
