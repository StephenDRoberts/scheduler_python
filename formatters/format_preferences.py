preferences_columns = {
    'Competition': 'competition',
    'Squad': 'squad'
}


def format_preferences(df):
    df = df.rename(columns=preferences_columns)

    preference_map = {}

    for index, row in df.iterrows():
        squad = row['squad']
        preference_list = preference_map.get(squad, [])
        preference_list.append(row['competition'])
        preference_map[squad] = preference_list

    return df
