preferences_columns = {
    'Competition': 'competition',
    'Squad': 'squad'
}


def format_preferences(df):
    df = df.rename(columns=preferences_columns)

    return df
