import pandas as pd

from src.formatters.format_competitions import format_competitions

competitions = pd.DataFrame({
    'Country': ['England', 'England', 'FIFA,Women\'s'],
    'Competition': ['Championship', 'Premier League', 'World Cup'],
    'Priority': [1, 1, 1]
})


def test_should_relabel_competitions_df():
    expected = pd.DataFrame({
        'country': competitions['Country'],
        'competition': competitions['Competition'],
        'priority_class': competitions['Priority']
    })

    result = format_competitions(competitions)

    pd.testing.assert_frame_equal(result, expected)


def test_should_not_format_label_not_in_dictionary():
    unused_label_competitions = pd.DataFrame({
    'Country': ['England', 'England', 'FIFA,Women\'s'],
    'Competition': ['Championship', 'Premier League', 'World Cup'],
    'Priority': [1, 1, 1],
    'New Label': [2, 2, 2]
})

    expected = pd.DataFrame({
        'country': unused_label_competitions['Country'],
        'competition': unused_label_competitions['Competition'],
        'priority_class': unused_label_competitions['Priority'],
        'New Label': unused_label_competitions['New Label'],
    })

    result = format_competitions(unused_label_competitions)

    pd.testing.assert_frame_equal(result, expected)
