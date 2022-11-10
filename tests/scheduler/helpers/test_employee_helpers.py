from datetime import timedelta, datetime

import numpy as np
import pandas as pd
import pytest

from constants.constants import AVERAGE_GAME_TIME_IN_MINUTES, SECONDS_IN_ONE_HOUR
from scheduler.helpers.employee_helpers import calculate_task_partial_hours_complete, get_employee_task_end_time, \
    calculate_task_completion_percentage
from tests.utils import create_empty_task_df

now = datetime.now()


#
# def timetable_builder(start, end, employee_id='employee-D+-2019-04-01-3'):
#     return pd.DataFrame({
#         'employee': [employee_id],
#         'match_id': ['match_1'],
#         'team': ['HOME'],
#         'process_start': [pd.to_datetime(start)],
#         'employee_process_end': [pd.to_datetime(end)]
#     })
#
#
# def task_builder(kick_off):
#     kick_off_datetime = pd.to_datetime(kick_off)
#     earliest_processing_datetime = kick_off_datetime + timedelta(minutes=110)
#     processing_deadline = kick_off_datetime + timedelta(hours=12)
#
#     return pd.Series(
#         ['match-1', 'HOME', kick_off_datetime, earliest_processing_datetime, 'Premier League', 'England', 1, 12,
#          processing_deadline],
#         index=['match_id', 'team', 'kick_off_datetime', 'earliest_processing_datetime', 'competition', 'country',
#                'priority_class', 'priority_hours', 'processing_deadline']
#     )
#
#
# # return pd.DataFrame({
# #     'match_id': ['match-1'],
# #     'team': ['HOME'],
# #     'kick_off_datetime': [kick_off_datetime],
# #     'earliest_processing_datetime': [earliest_processing_datetime],
# #     'competition': ['Premier League'],
# #     'country': ['England'],
# #     'priority_class': [1],
# #     'priority_hours': [12],
# #     'processing_deadline': [processing_deadline]
# # })
#
# employee = pd.Series(
#     [4, 'Night', '2019-04-01', 'D+', pd.to_datetime('2019-04-01 18:00:00'), pd.to_datetime('2019-04-02 02:00:00'),
#      'employee-D+-2019-04-01-3'],
#     index=['quantity', 'shift', 'date', 'squad', 'shift_start_datetime', 'shift_end_datetime', 'employee']
# )
#
# empty_timetable_df = pd.DataFrame(columns=['employee', 'match_id', 'team', 'process_start', 'employee_process_end'])
#
#
# class TestHasEmptyShift:
#
#     def test_returns_true_when_timetable_is_empty(self):
#         result = has_empty_shift(employee_shift_timetable=empty_timetable_df)
#         assert result is True
#
#     def test_returns_false_when_assigned_task_in_shift(self):
#         start = '2019-04-01 20:00:00'
#         end = '2019-04-02 00:00:00'
#         timetable = timetable_builder(start, end)
#         result = has_empty_shift(employee_shift_timetable=timetable)
#         assert result is False
#
#
# class TestHasTimeBeforeEndOfShift:
#     def test_returns_true_when_scheduled_task_ends_before_shift_end(self):
#         start = '2019-04-01 20:00:00'
#         end = '2019-04-02 00:00:00'
#         timetable = timetable_builder(start, end)
#         result = has_time_before_end_of_shift(employee=employee, employee_shift_timetable=timetable)
#         assert result is True
#
#
# # TODO consider moving defition of timetable/scheduled tasks etc
#
# class TestHasTimeBeforeScheduledTask:
#     def test_returns_true_when_employee_free_at_start(self):
#         timetable = timetable_builder(
#             start='2019-04-01 22:00:00', end='2019-04-02 02:00:00'
#         )
#
#         task = task_builder(kick_off='2019-04-01 16:00:00')
#         result = has_time_before_scheduled_task(employee=employee, employee_shift_timetable=timetable, task=task)
#         assert result is True
#
#     def test_returns_false_when_employee_is_not_free_at_start(self):
#         timetable = timetable_builder(
#             start='2019-04-01 19:00:00', end='2019-04-01 23:00:00'
#         )
#         task = task_builder(kick_off='2019-04-01 16:00:00')
#         result = has_time_before_scheduled_task(employee=employee, employee_shift_timetable=timetable, task=task)
#         assert result is False
#
#
# class TestFilterForEmployeeTimetable:
#     def test_returns_employee_timetable_from_timetable_df(self):
#         employee_1_timetable = timetable_builder(
#             start='2019-04-01 20:00:00', end='2019-04-02 00:00:00', employee_id='employee-A-2019-04-01-1'
#         )
#         employee_2_timetable = timetable_builder(
#             start='2019-04-01 20:00:00', end='2019-04-02 00:00:00', employee_id='employee-D+-2019-04-01-3'
#         )
#         timetable_df = pd.concat([employee_1_timetable, employee_2_timetable])
#
#         result = filter_for_employee_timetable_in_shift(employee=employee, employee_shift_timetable=timetable_df)
#         num_results = len(result.index)
#
#         pd.testing.assert_frame_equal(result, employee_2_timetable)
#         assert num_results == 1
#
#
class TestCalculatePartialHours:
    def test_returns_0_when_no_partial_records(self):
        empty_df = create_empty_task_df()

        result = calculate_task_partial_hours_complete(empty_df)

        assert result == 0

    def test_returns_calculated_hours_when_has_partial_records(self):
        process_start_1 = now - timedelta(hours=12)
        process_end_1 = now - timedelta(hours=11.5)

        process_start_2 = now - timedelta(hours=4)
        process_end_2 = now - timedelta(hours=2.5)

        rate_1 = 0.8
        rate_2 = 1.0

        df = pd.DataFrame(data={
            'task_id': ['match_1_HOME', 'match_1_HOME'],
            'match_id': ['match_1', 'match_1'],
            'team': ['team_HOME', 'team_HOME'],
            'kick_off_datetime': [now, now],
            'earliest_processing_datetime': [
                now + timedelta(hours=AVERAGE_GAME_TIME_IN_MINUTES),
                now + timedelta(hours=AVERAGE_GAME_TIME_IN_MINUTES)
            ],
            'competition': ['Premier League', 'Premier League'],
            'percentage_complete': [0.1, 0.475],
            'country': ['England', 'England'],
            'priority_class': [1, 1],
            'priority_hours': [12, 12],
            'processing_deadline': [now + timedelta(hours=12), now + timedelta(hours=12)],
            'process_start': [process_start_1, process_start_2],
            'process_end': [process_end_1, process_end_2],
            'rate': [rate_1, rate_2]
        })

        # (1) 0.5hrs * 0.8 + (2) 1.5hrs * 1.0 = 1.9
        expected_hours_complete = 1.9
        result = calculate_task_partial_hours_complete(df)

        assert result == expected_hours_complete


class TestCalculateEmployeeTaskStartEndTimes:
    def test_returns_shift_end_when_not_enough_time_to_complete_task(self):
        employee_task_start = pd.to_datetime('2019-04-0117:30', format='%Y-%m-%d%H:%M')
        hours_to_complete = 1
        shift_end = pd.to_datetime('2019-04-0118:00', format='%Y-%m-%d%H:%M')

        result = get_employee_task_end_time(employee_task_start, hours_to_complete, shift_end)

        assert result == shift_end

    def test_returns_task_end_when_enough_time_to_complete_task(self):
        employee_task_start = pd.to_datetime('2019-04-0119:15', format='%Y-%m-%d%H:%M')
        hours_to_complete = 0.5
        shift_end = pd.to_datetime('2019-04-0202:00', format='%Y-%m-%d%H:%M')

        expected = employee_task_start + timedelta(hours=hours_to_complete)

        result = get_employee_task_end_time(employee_task_start, hours_to_complete, shift_end)

        assert result == expected

#     def test_get_employee_task_start_time(self):

class TestCalculateTaskCompletionPercentage:
    def test_returns_0_if_start_time_equals_end(self):
        task_time = pd.to_datetime('2019-04-0119:15', format='%Y-%m-%d%H:%M')
        hours_to_complete = 1.5

        result = calculate_task_completion_percentage(task_time, task_time, hours_to_complete)

        assert result == 0

    def test_returns_0_if_start_time_after_than_end_time(self):
        start_time = pd.to_datetime('2019-04-0119:45', format='%Y-%m-%d%H:%M')
        end_time = pd.to_datetime('2019-04-0119:10', format='%Y-%m-%d%H:%M')
        hours_to_complete = 1.5

        result = calculate_task_completion_percentage(start_time, end_time, hours_to_complete)

        assert result == 0

    def test_returns_percentage_if_start_time_less_than_end_time(self):
        start_time = pd.to_datetime('2019-04-0119:15', format='%Y-%m-%d%H:%M')
        end_time = pd.to_datetime('2019-04-0119:30', format='%Y-%m-%d%H:%M')
        hours_to_complete = 1.5

        result = calculate_task_completion_percentage(start_time, end_time, hours_to_complete)

        assert result == pytest.approx(0.167, 0.01)

