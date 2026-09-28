from horizonlink.search.grid import maximize


def test_grid_search():
    params, score = maximize(lambda x, y: -(x - 2) ** 2 - (y - 3) ** 2, {"x": [1, 2, 3], "y": [2, 3, 4]})
    assert params == {"x": 2, "y": 3}
    assert score == 0
