import pandas as pd

from src.formatters.format_schedule import format_schedule

schedule = pd.DataFrame({
    'Quantity': [2, 1],
    'Shift': ['Morning', 'Night'],
    'Date': ['2019-04-01', '2019-04-02'],
    'Squad': ['A', 'B']
})


def test_should_format_schedule_df():
    shift_a_start_time = pd.to_datetime('2019-04-01' + '10:00', format='%Y-%m-%d%H:%M')
    shift_a_end_time = pd.to_datetime('2019-04-01' + '18:00', format='%Y-%m-%d%H:%M')
    shift_b_start_time = pd.to_datetime('2019-04-02' + '18:00', format='%Y-%m-%d%H:%M')
    shift_b_end_time = pd.to_datetime('2019-04-03' + '02:00', format='%Y-%m-%d%H:%M')

    expected = pd.DataFrame({
        'quantity': [2, 2, 1],
        'shift': ['Morning', 'Morning', 'Night'],
        'date': ['2019-04-01', '2019-04-01', '2019-04-02'],
        'squad': ['A', 'A', 'B'],
        'shift_start_datetime': [shift_a_start_time, shift_a_start_time, shift_b_start_time],
        'shift_end_datetime': [shift_a_end_time, shift_a_end_time, shift_b_end_time],
        'employee': ['employee-A-2019-04-01-Morning-1', 'employee-A-2019-04-01-Morning-2',
                     'employee-B-2019-04-02-Night-1']
    })

    result = format_schedule(schedule)

    pd.testing.assert_frame_equal(result, expected)
