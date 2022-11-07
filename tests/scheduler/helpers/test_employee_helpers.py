import numpy as np
import pandas as pd

from scheduler.helpers.employee_helpers import has_empty_shift, filter_for_employee_timetable_in_shift, \
    has_time_before_end_of_shift


def timetable_builder(start, end, employee_name='employee-D+-2019-04-01-3'):
    return pd.DataFrame({
        'employee': [employee_name],
        'match_id': ['match_1'],
        'team': ['HOME'],
        'process_start': [pd.to_datetime(start)],
        'employee_process_end': [pd.to_datetime(end)]
    })


employee = pd.Series(
    [4, 'Night', '2019-04-01', 'D+', pd.to_datetime('2019-04-01 18:00:00'), pd.to_datetime('2019-04-02 02:00:00'),
     'employee-D+-2019-04-01-3'],
    index=['quantity', 'shift', 'date', 'squad', 'shift_start_datetime', 'shift_end_datetime', 'employee']
)

empty_timetable_df = pd.DataFrame(columns=['employee', 'match_id', 'team', 'process_start', 'employee_process_end'])


class TestHasEmptyShift:
    def test_returns_true_when_employee_if_free_during_shift(self):
        start = '2019-03-01 18:00:00'
        end = '2019-03-01 22:00:00'
        timetable = timetable_builder(start, end)

        result = has_empty_shift(employee=employee, employee_shift_timetable=timetable)
        assert result is np.True_

    def test_returns_true_when_timetable_is_empty(self):
        result = has_empty_shift(employee=employee, employee_shift_timetable=empty_timetable_df)
        assert result is np.True_

    def test_returns_false_when_assigned_task_in_shift(self):
        start = '2019-04-01 20:00:00'
        end = '2019-04-02 00:00:00'
        timetable = timetable_builder(start, end)
        result = has_empty_shift(employee=employee, employee_shift_timetable=timetable)
        assert result is np.False_


class TestHasTimeBeforeEndOfShift:
    def test_returns_true_when_scheduled_task_ends_before_shift_end(self):
        start = '2019-04-01 20:00:00'
        end = '2019-04-02 00:00:00'
        timetable = timetable_builder(start, end)
        result = has_time_before_end_of_shift(employee=employee, employee_shift_timetable=timetable)
        assert result is True


class TestFilterForEmployeeTimetable:
    def test_returns_employee_timetable_from_timetable_df(self):
        employee_1_timetable = timetable_builder(
            start='2019-04-01 20:00:00', end='2019-04-02 00:00:00', employee_name='employee-A-2019-04-01-1'
        )
        employee_2_timetable = timetable_builder(
            start='2019-04-01 20:00:00', end='2019-04-02 00:00:00', employee_name='employee-D+-2019-04-01-3'
        )
        timetable_df = pd.concat([employee_1_timetable, employee_2_timetable])

        result = filter_for_employee_timetable_in_shift(employee=employee, employee_shift_timetable=timetable_df)
        num_results = len(result.index)

        pd.testing.assert_frame_equal(result, employee_2_timetable)
        assert num_results == 1
