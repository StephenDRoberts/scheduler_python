import pandas as pd

from datetime import timedelta

from src.constants.constants import MIN_TASK_DURATION_HOURS, SECONDS_IN_ONE_HOUR, NON_PREFERENCE_TIME_ADJUSTMENT_HOURS


def task_planner(employee, current_schedule_df, task, preference_squad):
    # calculate employee's rate of completion
    rate = calculate_rate(employee['squad'], preference_squad)

    # calculate amount of task already completed
    partial_records_for_task = current_schedule_df[current_schedule_df['task_id'] == task['task_id']]
    partially_completed_hours = calculate_task_partial_hours_complete(partial_records_for_task)
    hours_to_complete = (MIN_TASK_DURATION_HOURS - partially_completed_hours) / rate

    # get collectors scheduled task in shift (employee ids are unique to each shift)
    employee_timetable = current_schedule_df[current_schedule_df['employee'] == employee['employee']]
    shift_end = employee['shift_end_datetime']

    # check earliest time task can be picked up, and corresponding end time
    employee_task_start = get_employee_task_start_time(
        task, partial_records_for_task, employee, employee_timetable, hours_to_complete
    )

    employee_task_end = get_employee_task_end_time(employee_task_start, hours_to_complete, shift_end)

    # calculate percentage of task complete
    percentage_of_task_complete = calculate_task_completion_percentage(
        employee_task_start, employee_task_end, hours_to_complete)

    # return employees potential work plan for this task
    employee['employee_task_start'] = employee_task_start
    employee['employee_task_end'] = employee_task_end
    employee['rate'] = rate
    employee['percentage_complete'] = round(percentage_of_task_complete, 3)

    return employee


def get_employee_task_start_time(task, partial_records_for_task, employee, employee_timetable, hours_to_complete):
    # check earliest time task can be picked up
    time_task_is_ready_for_process = task['earliest_processing_datetime']
    shift_start = employee['shift_start_datetime']

    earliest_processing_start_given_shift_and_schedule = \
        get_earliest_processing_time_give_shift_and_start_time(
            time_task_is_ready_for_process, shift_start, partial_records_for_task
        )
    # if employee_timetable is empty -> assign earliest time to task
    if employee_timetable.empty:
        employee_start = earliest_processing_start_given_shift_and_schedule
    else:
        # get scheduled task start and end times
        employee_scheduled_task_start = min(employee_timetable['process_start'])
        employee_scheduled_task_end = max(employee_timetable['process_end'])

        # can this task be completed before scheduled task employee_scheduled_task_start
        earliest_potential_end_time = \
            earliest_processing_start_given_shift_and_schedule + timedelta(hours=hours_to_complete)

        if earliest_potential_end_time <= employee_scheduled_task_start:
            employee_start = earliest_processing_start_given_shift_and_schedule
        else:
            employee_start = employee_scheduled_task_end

    return employee_start


def get_earliest_processing_time_give_shift_and_start_time(
        time_task_is_ready_for_process, shift_start, partial_records_for_task
):
    return pd.concat([
        pd.Series({'start': shift_start}),
        pd.Series({'start': time_task_is_ready_for_process}),
        partial_records_for_task['process_end'].rename('start')
    ]).max()


def get_employee_task_end_time(employee_task_start, hours_to_complete, shift_end):
    full_completion_time = employee_task_start + timedelta(hours=hours_to_complete)
    return min(shift_end, full_completion_time)


def calculate_task_completion_percentage(employee_task_start, employee_task_end, hours_to_complete):
    task_duration = timedelta.total_seconds(employee_task_end - employee_task_start) / SECONDS_IN_ONE_HOUR
    percentage_of_task_complete = task_duration / hours_to_complete if task_duration > 0.0 else 0.0

    return percentage_of_task_complete


def calculate_task_partial_hours_complete(partial_records_for_task):
    return 0 if partial_records_for_task.empty else \
        timedelta.total_seconds(
            ((partial_records_for_task['process_end'] - partial_records_for_task['process_start']) *
             partial_records_for_task['rate']).sum()
        ) / SECONDS_IN_ONE_HOUR


def calculate_rate(employee_squad, preference_squad):
    if employee_squad == preference_squad:
        return 1
    else:
        return MIN_TASK_DURATION_HOURS / (MIN_TASK_DURATION_HOURS + NON_PREFERENCE_TIME_ADJUSTMENT_HOURS)
