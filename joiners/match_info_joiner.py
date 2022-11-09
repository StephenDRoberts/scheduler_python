import pandas as pd


def combine_match_info(matches_df, competitions_df, priorities_df):
    matches_with_competitions_df = pd.merge(
        matches_df[['match_id', 'team', 'kick_off_datetime', 'earliest_processing_datetime', 'competition']],
        competitions_df[['country', 'priority_class', 'competition']],
        on='competition'
    )

    combined_match_info_df = pd.merge(
        matches_with_competitions_df,
        priorities_df,
        on='priority_class'
    )

    combined_match_info_df['processing_deadline'] = combined_match_info_df['kick_off_datetime'] + pd.TimedeltaIndex(
        combined_match_info_df['priority_hours'], unit='h')

    # combined_match_info_df['processing_deadline'] = pd.to_datetime(combined_match_info_df['kick_off_datetime'],
    #                                                                format='%d/%m/%Y%H:%M') + \
    #                                                 timedelta(hours=combined_match_info_df['priority_hours'])

    return combined_match_info_df
