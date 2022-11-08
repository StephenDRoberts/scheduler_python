from datetime import timedelta

TASK_DURATION_HOURS = 4
TASK_DURATION_HOURS_NON_PREFERENCE = 5


def is_available_for_task(employee, timetable_df, task, preference_squad):
    employee_timetable = timetable_df[timetable_df['employee'] == employee['employee']]
    competition = task['competition']
    rate_of_completion = 1.0 if competition == preference_squad else \
        (TASK_DURATION_HOURS / TASK_DURATION_HOURS_NON_PREFERENCE)

    if has_empty_shift(employee_timetable):
        return True

    elif has_time_before_end_of_shift(employee, employee_timetable):
        # the employee can fit in all or partial amount before the end of their shift
        return True
    elif has_time_before_scheduled_task(employee, employee_timetable, task, rate_of_completion):
        # the employee has time earlier in their shift to complete a full review of a team
        return True
    else:
        return False


def calculate_pickup_and_completion_time(employee, timetable_df, task, rate):
    employee_timetable = timetable_df[timetable_df['employee'] == employee['employee']]

    if has_empty_shift(employee_timetable):
        start = max(task['earliest_processing_datetime'], employee['shift_start_datetime'])
        end = start + timedelta(hours=(TASK_DURATION_HOURS / rate)
        return {
            'start': start,
            'end': end
        }

    if has_time_before_end_of_shift(employee, employee_timetable, task):
        employee_shift_end = employee['shift_end_datetime']
        latest_scheduled_task_end = employee_timetable['employee_process_end'].max()

        start = max([employee_shift_end], latest_scheduled_task_end)
        end = employee_shift_end
        return {
            'start': start,
            'end': end
        }

    if has_time_before_scheduled_task(employee, employee_timetable, task):
        start = employee['shift_start_datetime']
        end = start + timedelta(hours=TASK_DURATION_HOURS)

        return {
            'start': start,
            'end': end
        }
    return None


def has_empty_shift(employee_shift_timetable):
    return employee_shift_timetable.empty


def has_time_before_end_of_shift(employee, employee_shift_timetable):
    employee_shift_end = employee['shift_end_datetime']
    scheduled_task_end_series = employee_shift_timetable['employee_process_end']
    return (scheduled_task_end_series.max() < employee_shift_end)


def has_time_before_scheduled_task(employee, employee_shift_timetable, task, rate):
    employee_shift_start = employee['shift_start_datetime']
    earliest_processing_time = task['earliest_processing_datetime']
    scheduled_tasks = employee_shift_timetable['process_start']

    return (scheduled_tasks.min() >= (employee_shift_start + timedelta(
        hours=(TASK_DURATION_HOURS / rate)))) and (earliest_processing_time <= employee_shift_start)


def filter_for_employee_timetable_in_shift(employee, employee_shift_timetable):
    return employee_shift_timetable[employee_shift_timetable['employee'] == employee['employee']]
