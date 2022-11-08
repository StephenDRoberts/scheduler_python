from datetime import timedelta

TASK_DURATION_HOURS = 4


def is_available_for_task(employee, timetable_df, task):
    employee_timetable = timetable_df[timetable_df['employee'] == employee['employee']]

    if has_empty_shift(employee_timetable):
        return True

    elif has_time_before_end_of_shift(employee, employee_timetable):
        # the employee can fit in all or partial amount before the end of their shift
        return True
    elif has_time_before_scheduled_task(employee, employee_timetable, task):
        # the employee has time earlier in their shift to complete a full review of a team
        return True
    else:
        return False

def has_empty_shift(employee_shift_timetable):
    return employee_shift_timetable.empty


def has_time_before_end_of_shift(employee, employee_shift_timetable):
    employee_shift_end = employee['shift_end_datetime']
    return (employee_shift_timetable['employee_process_end'].max() < employee_shift_end)


def has_time_before_scheduled_task(employee, employee_shift_timetable, task):
    employee_shift_start = employee['shift_start_datetime']
    earliest_processing_time = task['earliest_processing_datetime']
    scheduled_tasks = employee_shift_timetable['process_start']

    return (scheduled_tasks.min() >= (employee_shift_start + timedelta(
        hours=TASK_DURATION_HOURS))) and (earliest_processing_time <= employee_shift_start)


def filter_for_employee_timetable_in_shift(employee, employee_shift_timetable):
    return employee_shift_timetable[employee_shift_timetable['employee'] == employee['employee']]
