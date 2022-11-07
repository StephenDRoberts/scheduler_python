import pandas as pd
from datetime import timedelta


AVERAGE_GAME_TIME_IN_MINUTES = 110

match_columns = {
    'ID': 'match_id',
    'Match Date': 'match_date',
    'Kick-off Time': 'kick_off_time',
    'Competition': 'competition'
}


def format_matches_to_tasks(df):
    df = df.rename(columns=match_columns)

    df['competition'] = df['competition'].apply(lambda x: x.encode('latin-1').decode('utf-8'))

    kick_off_datetime = pd.to_datetime(df['match_date'] + df['kick_off_time'], format='%d/%m/%Y%H:%M')
    df['kick_off_datetime'] = kick_off_datetime

    earliest_processing_datetime = kick_off_datetime + timedelta(minutes=AVERAGE_GAME_TIME_IN_MINUTES)
    df['earliest_processing_datetime'] = earliest_processing_datetime

    tasks_df = pd.DataFrame(columns=df.columns.tolist() + ['team'])

    for index, row in df.iterrows():
        for i in range(2):
            team_association = "HOME" if i == 0 else "AWAY"
            data = pd.DataFrame([row])
            data['team'] = f'team-{team_association}'

            tasks_df = pd.concat([tasks_df, data], ignore_index=True)

    return tasks_df
