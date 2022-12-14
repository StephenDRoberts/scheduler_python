from datetime import datetime, timedelta

import pandas as pd

from src.constants.constants import AVERAGE_GAME_TIME_IN_MINUTES

now = datetime.now()

default_entries = [{
    'task_id': ['match_1_HOME'],
    'match_id': ['match_1'],
    'team': ['team_HOME'],
    'kick_off_datetime': [now],
    'earliest_processing_datetime': [now + timedelta(hours=AVERAGE_GAME_TIME_IN_MINUTES)],
    'competition': ['Premier League'],
    'percentage_complete': [0],
    'country': ['England'],
    'priority_class': [1],
    'priority_hours': [12],
    'processing_deadline': [now + timedelta(hours=12)],
    'process_start': [now],
    'process_end': [now + timedelta(hours=4)],
    'rate': 1.0
}]


def create_empty_task_df():
    df = pd.DataFrame(default_entries[0])
    cleared_df = df.iloc[0:0]

    return cleared_df
