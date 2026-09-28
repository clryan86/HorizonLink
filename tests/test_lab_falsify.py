from horizonlink.lab.falsify import falsify_candidate


def test_known_redshift_relationship_survives_controls():
    # In the current exterior-link model received power fraction and received
    # power differ by fixed transmitter power; with default P_tx=1 they are
    # exactly linear. This is intentionally a known/trivial relation used to
    # verify the falsifier, not a discovery.
    result=falsify_candidate(
        x='exterior_link.received_power_fraction',
        y='exterior_link.received_power_w',
        model='linear',
        controls={'mass_solar':[5.0,10.0,30.0],'bandwidth_hz':[1e3,1e6]},
    )
    assert result['summary']['successful_fits']>0
    assert result['summary']['minimum_r2']>0.999999
