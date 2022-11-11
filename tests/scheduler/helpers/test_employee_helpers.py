from datetime import timedelta, datetime

import pandas as pd
import pytest

from src.constants.constants import AVERAGE_GAME_TIME_IN_MINUTES, MIN_TASK_DURATION_HOURS, \
    NON_PREFERENCE_TIME_ADJUSTMENT_HOURS
from src.scheduler.helpers.create_empty_dataframes import create_empty_df_from_template
from src.scheduler.helpers.employee_helpers import calculate_task_completion_percentage, task_planner, \
    get_earliest_processing_time_give_shift_and_start_time, get_employee_task_end_time, calculate_rate, \
    calculate_task_partial_hours_complete

from tests.utils import create_empty_task_df

now = datetime.now()


def timetable_builder(start, end, task_id, rate, employee_id='employee-D+-2019-04-01-3'):
    hours_to_complete = MIN_TASK_DURATION_HOURS if rate == 1 else \
        MIN_TASK_DURATION_HOURS + NON_PREFERENCE_TIME_ADJUSTMENT_HOURS

    return pd.DataFrame({
        'employee': [employee_id],
        'task_id': [task_id],
        'match_id': ['match_1'],
        'team': ['HOME'],
        'process_start': [start],
        'process_end': [end],
        'rate': [rate],
        'percentage_complete': [calculate_task_completion_percentage(start, end, hours_to_complete)]
    })


def task_builder(task_id, kick_off):
    kick_off_datetime = pd.to_datetime(kick_off)
    earliest_processing_datetime = kick_off_datetime + timedelta(minutes=110)
    processing_deadline = kick_off_datetime + timedelta(hours=12)

    return pd.Series(
        [task_id, 'match-1', 'HOME', kick_off_datetime, earliest_processing_datetime, 'Premier League', 'England', 1,
         12,
         processing_deadline],
        index=['task_id', 'match_id', 'team', 'kick_off_datetime', 'earliest_processing_datetime', 'competition',
               'country', 'priority_class', 'priority_hours', 'processing_deadline']
    )


def employee_builder(start, end):
    return pd.Series(
        [4, 'Night', '2019-04-01', 'D+', start, end,
         'employee-D+-2019-04-01-3'],
        index=['quantity', 'shift', 'date', 'squad', 'shift_start_datetime', 'shift_end_datetime', 'employee']
    )


class TestTaskPlanner:

    def test_should_assign_task_to_start_of_shift_if_employee_has_no_tasks_scheduled(self):
        task = task_builder('task_1', pd.to_datetime('2019-03-31 20:00:00'))

        shift_start = pd.to_datetime('2019-04-01 18:00:00')
        shift_end = pd.to_datetime('2019-04-02 02:00:00')
        employee = employee_builder(shift_start, shift_end)

        # prev work on task lead to 3 hours of work done (75%)
        prev_task_start = pd.to_datetime('2019-03-31 23:00:00')
        prev_task_end = pd.to_datetime('2019-04-01 02:00:00')
        schedule = timetable_builder(prev_task_start, prev_task_end, 'task_1', 1, 'diff_employee')

        result = task_planner(employee, schedule, task, 'D+')

        expected = employee_builder(shift_start, shift_end)

        # only 1 hour of work needed, can be started straight away
        expected['employee_task_start'] = pd.to_datetime('2019-04-01 18:00:00')
        expected['employee_task_end'] = pd.to_datetime('2019-04-01 19:00:00')
        expected['rate'] = 1.0
        expected['percentage_complete'] = 1.0

        pd.testing.assert_series_equal(result, expected)

    def test_should_assign_task_to_end_of_employees_prev_scheduled_task_if_no_time_before_schedule_task(self):
        task = task_builder('task_1', pd.to_datetime('2019-03-31 20:00:00'))

        shift_start = pd.to_datetime('2019-04-01 18:00:00')
        shift_end = pd.to_datetime('2019-04-02 02:00:00')
        employee = employee_builder(shift_start, shift_end)

        # prev work on task lead to 3 hours of work done (75%)
        prev_task_start = pd.to_datetime('2019-03-31 23:00:00')
        prev_task_end = pd.to_datetime('2019-04-01 02:00:00')
        employee_diff_task_start = pd.to_datetime('2019-04-01 18:00:00')
        employee_diff_task_end = pd.to_datetime('2019-04-01 22:00:00')

        schedule = timetable_builder(prev_task_start, prev_task_end, 'task_1', 1, 'diff_employee')
        employee_task_schedule = timetable_builder(employee_diff_task_start, employee_diff_task_end, 'task_2', 1, )
        schedule = pd.concat([schedule, employee_task_schedule])

        result = task_planner(employee, schedule, task, 'D+')

        expected = employee_builder(shift_start, shift_end)

        # only 1 hour of work needed, can be started straight away
        expected['employee_task_start'] = pd.to_datetime('2019-04-01 22:00:00')
        expected['employee_task_end'] = pd.to_datetime('2019-04-01 23:00:00')
        expected['rate'] = 1.0
        expected['percentage_complete'] = 1.0

        pd.testing.assert_series_equal(result, expected)

    def test_should_assign_task_before_other_scheduled_task_if_enough_time_to_complete(self):
        task = task_builder('task_1', pd.to_datetime('2019-03-31 20:00:00'))

        shift_start = pd.to_datetime('2019-04-01 18:00:00')
        shift_end = pd.to_datetime('2019-04-02 02:00:00')
        employee = employee_builder(shift_start, shift_end)

        # prev work on task lead to 3 hours of work done (75%)
        prev_task_start = pd.to_datetime('2019-03-31 23:00:00')
        prev_task_end = pd.to_datetime('2019-04-01 02:00:00')
        employee_diff_task_start = pd.to_datetime('2019-04-01 20:00:00')
        employee_diff_task_end = pd.to_datetime('2019-04-02 00:00:00')

        schedule = timetable_builder(prev_task_start, prev_task_end, 'task_1', 1, 'diff_employee')
        employee_task_schedule = timetable_builder(employee_diff_task_start, employee_diff_task_end, 'task_2', 1, )
        schedule = pd.concat([schedule, employee_task_schedule])

        result = task_planner(employee, schedule, task, 'D+')

        expected = employee_builder(shift_start, shift_end)

        # only 1 hour of work needed, can be started straight away
        expected['employee_task_start'] = pd.to_datetime('2019-04-01 18:00:00')
        expected['employee_task_end'] = pd.to_datetime('2019-04-01 19:00:00')
        expected['rate'] = 1.0
        expected['percentage_complete'] = 1.0

        pd.testing.assert_series_equal(result, expected)

    def test_should_return_0_percentage_if_cannot_pick_up_task(self):
        task = task_builder('task_1', pd.to_datetime('2019-03-31 20:00:00'))

        shift_start = pd.to_datetime('2019-04-01 18:00:00')
        shift_end = pd.to_datetime('2019-04-02 02:00:00')
        employee = employee_builder(shift_start, shift_end)

        # prev work on task lead to 0.25 hours of work done (6.25%)
        prev_task_start = pd.to_datetime('2019-04-01 01:45:00')
        prev_task_end = pd.to_datetime('2019-04-01 02:00:00')

        # employees other assigned tasks
        employee_diff_task_start1 = pd.to_datetime('2019-04-01 18:00:00')
        employee_diff_task_end1 = pd.to_datetime('2019-04-01 22:00:00')
        employee_diff_task_start2 = pd.to_datetime('2019-04-01 22:00:00')
        employee_diff_task_end2 = pd.to_datetime('2019-04-02 02:00:00')

        schedule = timetable_builder(prev_task_start, prev_task_end, 'task_1', 1, 'diff_employee')
        employee_task_schedule_1 = timetable_builder(employee_diff_task_start1, employee_diff_task_end1, 'task_2', 1)
        employee_task_schedule_2 = timetable_builder(employee_diff_task_start2, employee_diff_task_end2, 'task_2', 1)

        schedule = pd.concat([schedule, employee_task_schedule_1, employee_task_schedule_2])

        result = task_planner(employee, schedule, task, 'D+')

        expected = employee_builder(shift_start, shift_end)

        # # only 1 hour of work needed, can be started straight away
        expected['employee_task_start'] = pd.to_datetime('2019-04-02 02:00:00')
        expected['employee_task_end'] = pd.to_datetime('2019-04-02 02:00:00')
        expected['rate'] = 1.0
        expected['percentage_complete'] = 0.0

        pd.testing.assert_series_equal(result, expected)

    def test_should_assign_task_at_a_scheduled_task_(self):
        task = task_builder('task_1', pd.to_datetime('2019-03-31 20:00:00'))

        shift_start = pd.to_datetime('2019-04-01 18:00:00')
        shift_end = pd.to_datetime('2019-04-02 02:00:00')
        employee = employee_builder(shift_start, shift_end)

        # prev work on task lead to 3 hours of work done (75%)
        prev_task_start = pd.to_datetime('2019-03-31 23:00:00')
        prev_task_end = pd.to_datetime('2019-04-01 02:00:00')
        schedule = timetable_builder(prev_task_start, prev_task_end, 'task_1', 1, 'diff_employee')

        result = task_planner(employee, schedule, task, 'D+')

        expected = employee_builder(shift_start, shift_end)

        # only 1 hour of work needed, can be started straight away
        expected['employee_task_start'] = pd.to_datetime('2019-04-01 18:00:00')
        expected['employee_task_end'] = pd.to_datetime('2019-04-01 19:00:00')
        expected['rate'] = 1.0
        expected['percentage_complete'] = 1.0

        pd.testing.assert_series_equal(result, expected)


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


#
class TestEarliestProcessingTime:
    default_task_list = pd.DataFrame({
        'task': ['task_1', 'task_1'],
        'process_end': [
            pd.to_datetime('2019-04-0120:00', format='%Y-%m-%d%H:%M'),
            pd.to_datetime('2019-04-0120:00', format='%Y-%m-%d%H:%M')
        ]
    })

    default_time_task_is_ready_for_process = pd.to_datetime('2019-04-0120:00', format='%Y-%m-%d%H:%M')
    default_shift_start = pd.to_datetime('2019-04-0120:00', format='%Y-%m-%d%H:%M')

    def test_returns_task_ready_time_when_latest(self):
        later_ready_time = pd.to_datetime('2019-04-0210:00', format='%Y-%m-%d%H:%M')

        result = get_earliest_processing_time_give_shift_and_start_time(
            later_ready_time,
            self.default_shift_start,
            self.default_task_list
        )

        assert result == later_ready_time

    def test_returns_shift_start_when_latest(self):
        later_shift_start = pd.to_datetime('2019-04-0121:00', format='%Y-%m-%d%H:%M')

        result = get_earliest_processing_time_give_shift_and_start_time(
            self.default_time_task_is_ready_for_process,
            later_shift_start,
            self.default_task_list
        )

        assert result == later_shift_start

    def test_returns_latest_partial_record_end_when_latest(self):
        later_partial_records = pd.DataFrame({
            'task': ['task_1', 'task_1'],
            'process_end': [
                pd.to_datetime('2019-04-0121:00', format='%Y-%m-%d%H:%M'),
                pd.to_datetime('2019-04-0122:00', format='%Y-%m-%d%H:%M')
            ]
        })

        result = get_earliest_processing_time_give_shift_and_start_time(
            self.default_time_task_is_ready_for_process,
            self.default_shift_start,
            later_partial_records
        )

        assert result == pd.to_datetime('2019-04-0122:00', format='%Y-%m-%d%H:%M')

    def test_returns_latest_date_when_DataFrame_is_empty(self):
        empty_df = create_empty_df_from_template(self.default_task_list)

        result = get_earliest_processing_time_give_shift_and_start_time(
            self.default_time_task_is_ready_for_process,
            self.default_shift_start,
            empty_df
        )

        assert empty_df.empty
        assert result == pd.to_datetime('2019-04-0120:00', format='%Y-%m-%d%H:%M')


class TestCalculateEmployeeTaskEndTime:
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


class TestCalculateRate:
    def test_return_1_if_squad_matches_preference(self):
        assert calculate_rate('A', 'A') == 1.0

    def test_return_0pt8_if_squad_matches_preference(self):
        assert calculate_rate('A', 'B') == 0.8
