"""Fast pure-Python synthetic tests; no ROM or RMG required."""

import pytest

from tools.audit_audio_fifo_phase import (
    BUSY,
    HEADER,
    RECORD,
    analyze,
    cp0_delta,
    native_pcm_frames,
    read_trace,
)


def _event(seq, kind, cp0, *fields):
    return (seq, seq * 1000, kind, cp0, *(tuple(fields) + (0,) * (8 - len(fields))))


def test_native_frames_and_cp0_wraparound():
    assert native_pcm_frames(0) == 704
    assert native_pcm_frames(8) == 688
    assert native_pcm_frames(1_344) == 368
    assert native_pcm_frames(1_472) == 352
    assert cp0_delta(18, 0xFFFFFFFE) == 20
    assert cp0_delta(0xFFFFFFFE, 18) == -20


def test_one_native_buffer_reconstructed_exactly():
    vi = [_event(0, 0x20, 90)]
    ai = [
        _event(0, 0x12, 100, 0),
        _event(1, 0x13, 200, 0),
        _event(2, 0x10, 200, 0, 2816, 0, 0, 0, 1551616),
        _event(3, 0x11, 220, BUSY, 2816, 0, 1551616),
        _event(4, 0x12, 242, 2808),
    ]
    result = analyze(ai, vi)
    assert result["exact_ai_len_reads"] == 2
    assert result["exact_accepted_pcm_sizes"] == 1
    assert result["native_rejected_submissions"] == 0


def test_binary_trace_integrity_guard(tmp_path):
    p = tmp_path / "trace.bin"
    data = _event(0, 0x20, 90)
    p.write_bytes(HEADER.pack(b"MZRHST1\0", 1, RECORD.size, 1, 1, 0)
                  + RECORD.pack(*data))
    parsed, metadata = read_trace(p)
    assert parsed == [data]
    assert metadata["records"] == 1
    p.write_bytes(HEADER.pack(b"MZRHST1\0", 1, RECORD.size, 1, 2, 1)
                  + RECORD.pack(*data))
    with pytest.raises(ValueError, match="Incomplete"):
        read_trace(p)
