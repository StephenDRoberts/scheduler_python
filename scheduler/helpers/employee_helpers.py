from datetime import timedelta

TASK_DURATION_HOURS = 4
TASK_DURATION_HOURS_NON_PREFERENCE = 5
SECONDS_IN_HOURS = 60 * 60


def earmark_collector(collector, current_schedule_df, task, preference_squad):
    # calculate employees rate of completion
    rate = 1.0 if collector['squad'] == preference_squad else (TASK_DURATION_HOURS / TASK_DURATION_HOURS_NON_PREFERENCE)
    partial_record_for_task = current_schedule_df[current_schedule_df['task_id'] == task['task_id']]

    if task['match_id'] == 13810:
        print("partial_record_for_task")
        print(partial_record_for_task)

    partially_completed_hours = 0 if partial_record_for_task.empty else \
        timedelta.total_seconds(partial_record_for_task['process_end'].iloc[0] - partial_record_for_task['process_start'].iloc[0])/ SECONDS_IN_HOURS

    hours_to_complete = (TASK_DURATION_HOURS - partially_completed_hours) / rate


    # get collectors scheduled task (employee ids are unique to each shift)
    # TODO need to handle empty employee value rather than default to empty string
    collector_timetable = current_schedule_df[current_schedule_df['employee'] == collector['employee']]

    if task['match_id'] == 13810:
        print("collector_timetable")
        print(collector_timetable)

    # check earliest time task can be picked up
    time_task_is_ready_for_process = task['earliest_processing_datetime']
    shift_start = collector['shift_start_datetime']

    if partially_completed_hours == 0:
        earliest_processing_start_given_shift_and_schedule = max(time_task_is_ready_for_process, shift_start)
    else:
        earliest_processing_start_given_shift_and_schedule = max(
            time_task_is_ready_for_process, shift_start, partial_record_for_task['process_end'].iloc[0]
        )


    # if collector_timetable is empty -> assign earliest time to task
    if collector_timetable.empty:
        collector_start = earliest_processing_start_given_shift_and_schedule
    else:
        #   get scheduled task start and end times
        collectors_scheduled_task_start = min(collector_timetable['process_start'])
        collectors_scheduled_task_end = max(collector_timetable['process_end'])

        # TODO dont think this works now
        # Need to allow for task end time in the collectors start time
        # can this task be completed before scheduled task collectors_scheduled_task_start
        earliest_potential_end_time = earliest_processing_start_given_shift_and_schedule + timedelta(hours=hours_to_complete)

        if earliest_potential_end_time <= collectors_scheduled_task_start:
            collector_start = earliest_processing_start_given_shift_and_schedule
        else:
            collector_start = collectors_scheduled_task_end

    full_completion_time = collector_start + timedelta(hours=hours_to_complete)
    shift_end = collector['shift_end_datetime']
    collector_end = min(shift_end, full_completion_time)
    # calculate percentage of task complete
    task_duration = timedelta.total_seconds(collector_end - collector_start) / SECONDS_IN_HOURS
    percentage_of_task_complete = task_duration / hours_to_complete if task_duration != 0.0 else 0.0

    collector['collector_start'] = collector_start
    collector['collector_end'] = collector_end
    collector['percentage_complete'] = round(percentage_of_task_complete, 3)

    return collector


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
        end = start + timedelta(hours=(TASK_DURATION_HOURS / rate))
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
