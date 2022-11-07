from datetime import timedelta

TASK_DURATION_HOURS = 4


def is_available_for_task(employee, timetable_df, task):
    # print(employee)
    # print(task)
    earliest_processing_time = task['earliest_processing_datetime']
    employee_shift_start = employee['shift_start_datetime']
    employee_shift_end = employee['shift_end_datetime']


    if timetable_df.empty:
        return True
    #  TODO split into smaller helper functions
    elif earliest_processing_time >= timetable_df.max['employee_process_end'] and timetable_df.max[
        'employee_process_end'] != employee_shift_end:
        # the employee can fit in all or partial amount before the end of their shift
        return True
    elif (earliest_processing_time + timedelta(hours=TASK_DURATION_HOURS)) <= timetable_df.min['process_start'] and \
            timetable_df.min['process_start'] >= employee_shift_start:
        # the employee has time earlier in their shift to complete a full review of a team
        return True
    else:
        return False
