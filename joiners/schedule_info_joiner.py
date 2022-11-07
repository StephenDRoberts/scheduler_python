import pandas as pd


def combine_schedule_info(schedule_df, preferences_df):
    return pd.merge(
        schedule_df[['quantity', 'shift', 'shift_start_datetime', 'shift_end_datetime', 'squad']],
        preferences_df,
        on='squad'
    )
