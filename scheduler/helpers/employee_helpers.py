from datetime import timedelta

from constants.constants import MIN_TASK_DURATION_HOURS, SECONDS_IN_ONE_HOUR, NON_PREFERENCE_TIME_ADJUSTMENT_HOURS


def earmark_employee(employee, current_schedule_df, task, preference_squad, shift_index):
    # calculate employees rate of completion
    rate = 1.0 if employee['squad'] == preference_squad else (
                MIN_TASK_DURATION_HOURS / (MIN_TASK_DURATION_HOURS + NON_PREFERENCE_TIME_ADJUSTMENT_HOURS))
    partial_records_for_task = current_schedule_df[current_schedule_df['task_id'] == task['task_id']]

    partially_completed_hours = 0 if partial_records_for_task.empty else \
        timedelta.total_seconds(
            ((partial_records_for_task['process_end'] - partial_records_for_task['process_start']) *
             partial_records_for_task['rate']).sum()
        ) / SECONDS_IN_ONE_HOUR

    hours_to_complete = (MIN_TASK_DURATION_HOURS - partially_completed_hours) / rate

    # get collectors scheduled task (employee ids are unique to each shift)
    employee_timetable = current_schedule_df[current_schedule_df['employee'] == employee['employee']]
    shift_end = employee['shift_end_datetime']

    # check earliest time task can be picked up
    employee_task_start = get_employee_task_start_time(task, partial_records_for_task, employee, employee_timetable, hours_to_complete)
    employee_task_end = get_employee_task_end_time(employee_task_start, hours_to_complete, shift_end)

    # calculate percentage of task complete
    percentage_of_task_complete = calculate_task_completion_percentage(employee_task_start, employee_task_end, hours_to_complete)

    employee['employee_task_start'] = employee_task_start
    employee['employee_task_end'] = employee_task_end
    employee['rate'] = rate
    employee['percentage_complete'] = round(percentage_of_task_complete, 3)

    return employee


def get_employee_task_start_time(task, partial_records_for_task, employee, employee_timetable, hours_to_complete):
    # check earliest time task can be picked up
    time_task_is_ready_for_process = task['earliest_processing_datetime']
    shift_start = employee['shift_start_datetime']

    partially_completed_hours = calculate_task_partial_hours_complete(partial_records_for_task)

    if partially_completed_hours == 0:
        earliest_processing_start_given_shift_and_schedule = max(time_task_is_ready_for_process, shift_start)
    else:
        earliest_processing_start_given_shift_and_schedule = max(
            time_task_is_ready_for_process, shift_start, partial_records_for_task['process_end'].max()
        )

    # if employee_timetable is empty -> assign earliest time to task
    if employee_timetable.empty:
        employee_start = earliest_processing_start_given_shift_and_schedule
    else:
        #   get scheduled task start and end times
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
