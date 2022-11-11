import pandas as pd

from src.reporting.create_report import create


class TestCreateReport:
    def test_returns_correct_unique_match_stats(self):
        processed_df = pd.DataFrame({
            'task_id': ['task_1_HOME', 'task_1_AWAY', 'task_1_HOME', 'task_1_AWAY', 'task_2_HOME'],
            'match_id': ['match_1', 'match_1', 'match_1', 'match_1', 'match_2'],
            'percentage_complete': [0.5, 0.6, 1.0, 1.0, 1.0]
        })

        partial_df = pd.DataFrame({
            'task_id': ['task_3_HOME', 'task_4_AWAY'],
            'match_id': ['match_2', 'match_4'],
            'percentage_complete': [0.3, 0.4]
        })

        overdue_df = pd.DataFrame({
            'task_id': ['task_1_HOME', 'task_1_AWAY'],
            'match_id': ['match_1', 'match_1'],
            'percentage_complete': [1.0, 1.0]
        })

        expected = {
            'completed_matches': 1,
            'overdue_matches': 1,
            'partially_complete_matches': 2,
        }

        result = create({
            'processed_tasks': processed_df,
            'partially_processed_tasks': partial_df,
            'overdue_tasks': overdue_df
        })

        assert result == expected
