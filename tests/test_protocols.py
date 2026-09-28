from horizonlink.protocols.hayden_preskill import recovery_probability


def test_recovery_probability_increases_with_collected_qubits():
    low = recovery_probability(8, 8)
    high = recovery_probability(8, 24)
    assert high > low
    assert 0.0 < low < 1.0
    assert 0.0 < high < 1.0
