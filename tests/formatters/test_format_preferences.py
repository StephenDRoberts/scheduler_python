import pandas as pd

from src.formatters.format_preferences import format_preferences

preferences = pd.DataFrame({
    'Competition': ['Premier League', 'Championship'],
    'Squad': ['A', 'B'],
})


def test_should_relabel_competitions_df():
    expected = pd.DataFrame({
        'competition': preferences['Competition'],
        'squad': preferences['Squad'],
    })

    result = format_preferences(preferences)

    pd.testing.assert_frame_equal(result, expected)

    assert result[result['competition'] == 'Premier League']['squad'].item() == 'A'
    assert result[result['competition'] == 'Championship']['squad'].item() == 'B'
