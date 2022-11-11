from datetime import datetime, timedelta

import pandas as pd

from src.joiners.preferences_joiner import hydrate_preferences

now = datetime.now()


class TestMatchInfoJoiner:
    def test_returns_joined_df_with_required_columns(self):
        preferences_df = pd.DataFrame({
            'competition': ['Premier League'],
            'squad': ['A'],
        })

        competitions_df = pd.DataFrame({
            'country': ['England', 'Japan'],
            'priority_class': [1, 5],
            'competition': ['Premier League', 'unmatched_competition'],
        })

        expected = pd.DataFrame({
            'competition': ['Premier League', 'unmatched_competition'],
            'squad': ['A', 'not preferred'],
        })

        result = hydrate_preferences(preferences_df, competitions_df)

        pd.testing.assert_frame_equal(result, expected)
