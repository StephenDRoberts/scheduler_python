priorities_columns = {
    'Priority Class': 'priority_class',
    'Hours': 'priority_hours',
}


def format_priorities(df):
    df = df.rename(columns=priorities_columns)

    return df
