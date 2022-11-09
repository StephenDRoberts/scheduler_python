import pandas as pd

def hydrate_preferences(preferences_df, competitions_df):
    common = preferences_df.merge(competitions_df, on=['competition'])
    uncommon = competitions_df[(~competitions_df['competition'].isin(common['competition']))]

    uncommon_preferences_df = pd.DataFrame({
        'competition': uncommon['competition'],
        'squad': 'not preferred'
    })

    hydrated_preferences = pd.concat([preferences_df, uncommon_preferences_df])

    return hydrated_preferences
