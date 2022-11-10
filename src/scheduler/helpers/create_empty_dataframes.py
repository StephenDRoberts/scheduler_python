def create_empty_df_from_template(df, new_series_dict={}):
    new_df = df.copy(deep=False)
    new_df.astype(df.dtypes.to_dict())

    for key in new_series_dict:
        new_df[key] = new_series_dict[key]

    cleared_df = new_df.iloc[0:0]

    return cleared_df
