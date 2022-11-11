import pandas as pd

from src.formatters.format_matches import format_matches_to_tasks

matches = pd.DataFrame({
    'ID': ['46330', '49520'],
    'Match Date': ['01/04/2019', '02/05/2019'],
    'Kick-off Time': ['00:30', '15:00'],
    'Competition': ['MLS', 'Segunda DivisiÃ³n']
})


def test_should_format_matches_to_tasks_with_character_encoding():
    mls_kick_off_datetime = pd.to_datetime('01/04/2019' + '00:30', format='%d/%m/%Y%H:%M')
    mls_earliest_processing_time = pd.to_datetime('01/04/2019' + '02:20', format='%d/%m/%Y%H:%M')

    segunda_kick_off_datetime = pd.to_datetime('02/05/2019' + '15:00', format='%d/%m/%Y%H:%M')
    segunda_earliest_processing_time = pd.to_datetime('02/05/2019' + '16:50', format='%d/%m/%Y%H:%M')

    expected = pd.DataFrame({
        'match_id': ['46330', '46330', '49520', '49520'],
        'match_date': ['01/04/2019', '01/04/2019', '02/05/2019', '02/05/2019'],
        'kick_off_time': ['00:30', '00:30', '15:00', '15:00'],
        'competition': ['MLS', 'MLS', 'Segunda División', 'Segunda División'],
        'kick_off_datetime': [
            mls_kick_off_datetime, mls_kick_off_datetime, segunda_kick_off_datetime, segunda_kick_off_datetime
        ],
        'earliest_processing_datetime': [
            mls_earliest_processing_time, mls_earliest_processing_time, segunda_earliest_processing_time,
            segunda_earliest_processing_time
        ],
        'team': ['team-HOME', 'team-AWAY', 'team-HOME', 'team-AWAY'],
        'task_id': ['46330-HOME', '46330-AWAY', '49520-HOME', '49520-AWAY'],
        'percentage_complete': [0.0, 0.0, 0.0, 0.0]
    })

    result = format_matches_to_tasks(matches)

    pd.testing.assert_frame_equal(result, expected)
