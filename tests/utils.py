from datetime import datetime, timedelta

import pandas as pd

from constants.constants import AVERAGE_GAME_TIME_IN_MINUTES
from scheduler.helpers.create_empty_dataframes import create_empty_df_from_template

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


# def create_populated_task_df(entries=default_entries):
#     for entry in len(entries):
#         for key in entry:
#             default_entries[key] = entry[key]
#
#     return pd.DataFrame(entries_dict)


def create_empty_task_df():
    df = pd.DataFrame(default_entries[0])
    cleared_df = df.iloc[0:0]



    print(pd.concat([cleared_df['process_end'], pd.Series({'process_end': now})]).max())

    return cleared_df



