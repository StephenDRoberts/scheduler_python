from datetime import datetime, timedelta

import pandas as pd

from src.joiners.match_info_joiner import combine_match_info

now = datetime.now()


class TestMatchInfoJoiner:
    def test_returns_joined_df_with_required_columns(self):
        matches_df = pd.DataFrame({
            'task_id': ['task_1'],
            'match_id': ['match_1'],
            'team': ['HOME'],
            'kick_off_datetime': [now],
            'earliest_processing_datetime': [now],
            'competition': ['Premier League'],
            'percentage_complete': [0.5],
            'unnecessary_matches_column': [True]
        })

        competitions_df = pd.DataFrame({
            'country': ['England'],
            'priority_class': [1],
            'competition': ['Premier League'],
            'unnecessary_competition_column': [True]
        })

        priorities_df = pd.DataFrame({
            'priority_hours': [12],
            'priority_class': [1],
        })

        processing_deadline = now + timedelta(hours=12)

        expected = pd.DataFrame({
            'task_id': ['task_1'],
            'match_id': ['match_1'],
            'team': ['HOME'],
            'kick_off_datetime': [now],
            'earliest_processing_datetime': [now],
            'competition': ['Premier League'],
            'percentage_complete': [0.5],
            'country': ['England'],
            'priority_class': [1],
            'priority_hours': [12],
            'processing_deadline': [processing_deadline]
        })

        result = combine_match_info(matches_df, competitions_df, priorities_df)

        pd.testing.assert_frame_equal(result, expected)
