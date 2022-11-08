from datetime import timedelta

import numpy as np
import pandas as pd

from scheduler.helpers.employee_helpers import has_empty_shift, filter_for_employee_timetable_in_shift, \
    has_time_before_end_of_shift, has_time_before_scheduled_task


def timetable_builder(start, end, employee_id='employee-D+-2019-04-01-3'):
    return pd.DataFrame({
        'employee': [employee_id],
        'match_id': ['match_1'],
        'team': ['HOME'],
        'process_start': [pd.to_datetime(start)],
        'employee_process_end': [pd.to_datetime(end)]
    })


def task_builder(kick_off):
    kick_off_datetime = pd.to_datetime(kick_off)
    earliest_processing_datetime = kick_off_datetime + timedelta(minutes=110)
    processing_deadline = kick_off_datetime + timedelta(hours=12)

    return pd.Series(
        ['match-1', 'HOME', kick_off_datetime, earliest_processing_datetime, 'Premier League', 'England', 1, 12,
         processing_deadline],
        index=['match_id', 'team', 'kick_off_datetime', 'earliest_processing_datetime', 'competition', 'country',
               'priority_class', 'priority_hours', 'processing_deadline']
    )


# return pd.DataFrame({
#     'match_id': ['match-1'],
#     'team': ['HOME'],
#     'kick_off_datetime': [kick_off_datetime],
#     'earliest_processing_datetime': [earliest_processing_datetime],
#     'competition': ['Premier League'],
#     'country': ['England'],
#     'priority_class': [1],
#     'priority_hours': [12],
#     'processing_deadline': [processing_deadline]
# })

employee = pd.Series(
    [4, 'Night', '2019-04-01', 'D+', pd.to_datetime('2019-04-01 18:00:00'), pd.to_datetime('2019-04-02 02:00:00'),
     'employee-D+-2019-04-01-3'],
    index=['quantity', 'shift', 'date', 'squad', 'shift_start_datetime', 'shift_end_datetime', 'employee']
)

empty_timetable_df = pd.DataFrame(columns=['employee', 'match_id', 'team', 'process_start', 'employee_process_end'])


class TestHasEmptyShift:

    def test_returns_true_when_timetable_is_empty(self):
        result = has_empty_shift(employee_shift_timetable=empty_timetable_df)
        assert result is True

    def test_returns_false_when_assigned_task_in_shift(self):
        start = '2019-04-01 20:00:00'
        end = '2019-04-02 00:00:00'
        timetable = timetable_builder(start, end)
        result = has_empty_shift(employee_shift_timetable=timetable)
        assert result is False


class TestHasTimeBeforeEndOfShift:
    def test_returns_true_when_scheduled_task_ends_before_shift_end(self):
        start = '2019-04-01 20:00:00'
        end = '2019-04-02 00:00:00'
        timetable = timetable_builder(start, end)
        result = has_time_before_end_of_shift(employee=employee, employee_shift_timetable=timetable)
        assert result is True


# TODO consider moving defition of timetable/scheduled tasks etc

class TestHasTimeBeforeScheduledTask:
    def test_returns_true_when_employee_free_at_start(self):
        timetable = timetable_builder(
            start='2019-04-01 22:00:00', end='2019-04-02 02:00:00'
        )

        task = task_builder(kick_off='2019-04-01 16:00:00')
        result = has_time_before_scheduled_task(employee=employee, employee_shift_timetable=timetable, task=task)
        assert result is True

    def test_returns_false_when_employee_is_not_free_at_start(self):
        timetable = timetable_builder(
            start='2019-04-01 19:00:00', end='2019-04-01 23:00:00'
        )
        task = task_builder(kick_off='2019-04-01 16:00:00')
        result = has_time_before_scheduled_task(employee=employee, employee_shift_timetable=timetable, task=task)
        assert result is False


class TestFilterForEmployeeTimetable:
    def test_returns_employee_timetable_from_timetable_df(self):
        employee_1_timetable = timetable_builder(
            start='2019-04-01 20:00:00', end='2019-04-02 00:00:00', employee_id='employee-A-2019-04-01-1'
        )
        employee_2_timetable = timetable_builder(
            start='2019-04-01 20:00:00', end='2019-04-02 00:00:00', employee_id='employee-D+-2019-04-01-3'
        )
        timetable_df = pd.concat([employee_1_timetable, employee_2_timetable])

        result = filter_for_employee_timetable_in_shift(employee=employee, employee_shift_timetable=timetable_df)
        num_results = len(result.index)

        pd.testing.assert_frame_equal(result, employee_2_timetable)
        assert num_results == 1
