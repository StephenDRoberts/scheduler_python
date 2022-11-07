competition_columns = {
    'Country': 'country',
    'Competition': 'competition',
    'Priority': 'priority_class',
}


def format_competitions(df):
    df = df.rename(columns=competition_columns)

    return df
