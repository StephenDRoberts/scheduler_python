from datetime import timedelta

import numpy as np

TASK_DURATION_HOURS = 4


def is_available_for_task(employee, timetable_df, task):
    employee_timetable = timetable_df[timetable_df['employee'] == employee['employee']]
    earliest_processing_time = task['earliest_processing_datetime']
    employee_shift_start = employee['shift_start_datetime']
    employee_shift_end = employee['shift_end_datetime']



    if timetable_df.empty:
        return True
    #  TODO split into smaller helper functions
    # need to fix for earliest processing time during an allocated task and they have time afterwards to pick up
    elif earliest_processing_time >= employee_timetable.max['employee_process_end'] and employee_timetable.max[
        'employee_process_end'] != employee_shift_end:
        # the employee can fit in all or partial amount before the end of their shift
        return True
    elif (earliest_processing_time + timedelta(hours=TASK_DURATION_HOURS)) <= employee_timetable.min['process_start'] and \
            earliest_processing_time >= employee_shift_start and earliest_processing_time < employee_shift_end:
        # the employee has time earlier in their shift to complete a full review of a team
        return True
    else:
        return False


def has_empty_shift(employee, employee_shift_timetable):
    if employee_shift_timetable.empty:
        return np.True_
    else:
        employee_shift_start = employee['shift_start_datetime']
        employee_shift_end = employee['shift_end_datetime']
        return ~((employee_shift_timetable['process_start'] >= employee_shift_start) & (
                employee_shift_timetable['process_start'] < employee_shift_end)).all()


def has_time_before_end_of_shift(employee, employee_shift_timetable):
    employee_shift_end = employee['shift_end_datetime']
    return (employee_shift_timetable['employee_process_end'].max() < employee_shift_end)

def filter_for_employee_timetable_in_shift(employee, employee_shift_timetable):
    return employee_shift_timetable[employee_shift_timetable['employee'] == employee['employee']]
