from core.primordial import PrimordialEntity, PrimordialSimulation


def test_simulation_survives_default_entity():
    outcome = PrimordialSimulation().run(PrimordialEntity())

    assert outcome.survived is True
    assert outcome.retained_constants["love"] > 0.0
    assert outcome.retained_constants["life"] > 0.0
    assert outcome.emergent_order > 0.0
    assert len(outcome.stage_results) >= 1


def test_simulation_can_collapse_fragile_entity():
    entity = PrimordialEntity(
        name="fragile-entity",
        love=0.25,
        life=0.2,
        integrity=0.3,
        hope=0.2,
        truth=0.3,
    )

    outcome = PrimordialSimulation().run(entity)

    assert outcome.survived is False
    assert any(stage.status == "collapsed" for stage in outcome.stage_results)
