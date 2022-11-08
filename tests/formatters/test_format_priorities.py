import pandas as pd

from formatters.format_priorities import format_priorities

priorities = pd.DataFrame({
    'Priority Class': [1, 2, 3],
    'Hours': [12, 24, 48],
})


def test_should_relabel_competitions_df():
    expected = pd.DataFrame({
        'priority_class': priorities['Priority Class'],
        'priority_hours': priorities['Hours'],
    })

    result = format_priorities(priorities)

    pd.testing.assert_frame_equal(result, expected)

