import pandas as pd

# TODO Delete?
# def combine_schedule_info(schedule_df, preferences_df):
#     return pd.merge(
#         schedule_df[['quantity', 'shift', 'shift_start_datetime', 'shift_end_datetime', 'squad']],
#         preferences_df,
#         on='squad'
#     )

def hydrate_preferences(preferences_df, competitions_df):
    common = preferences_df.merge(competitions_df, on=['competition'])
    uncommon = competitions_df[(~competitions_df['competition'].isin(common['competition']))]

    uncommon_preferences_df = pd.DataFrame({
        'competition': uncommon['competition'],
        'squad': 'not preferred'
    })

    hydrated_preferences = pd.concat([preferences_df, uncommon_preferences_df])

    return hydrated_preferences
