"""Read-only RMG v04 audio deadline audit arithmetic tests (no ROM)."""

from tools.audit_audio_dma_deadlines import (
    COUNT_PER_BYTE,
    VI_COUNT,
    count_delta,
    deadline_margin,
)


def test_audio_quantization_is_near_one_vi_for_368_frames():
    assert 1472 * COUNT_PER_BYTE == 811072
    assert VI_COUNT - 811072 == 20
    assert VI_COUNT - 1408 * COUNT_PER_BYTE == 35284
    assert 1536 * COUNT_PER_BYTE - VI_COUNT == 35244
    assert (1472 - 1408) * COUNT_PER_BYTE == 35264


def test_opposite_observed_v04_forks_and_tail_counterfactual():
    # Slower capture's last FULL service is followed by empty FIFO and 352-loop.
    assert deadline_margin(735301597, 734490209, 1408) == 35580
    assert deadline_margin(735301597, 734490209, 1472) == 316
    # Fast capture's 1472-byte queued buffer remains active next service.
    assert deadline_margin(121069894, 120262948, 1472) == -4126
    assert deadline_margin(121069894, 120262948, 1408) == 31138


def test_count_wraparound_and_sign():
    assert count_delta(2, 0xFFFFFFFE) == 4
    assert count_delta(0xFFFFFFFE, 2) == -4
