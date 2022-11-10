from datetime import timedelta

from constants.constants import MIN_TASK_DURATION_HOURS, SECONDS_IN_HOURS, NON_PREFERENCE_TIME_ADJUSTMENT_HOURS


def earmark_collector(collector, current_schedule_df, task, preference_squad, shift_index):
    # calculate employees rate of completion
    rate = 1.0 if collector['squad'] == preference_squad else (MIN_TASK_DURATION_HOURS / (MIN_TASK_DURATION_HOURS + NON_PREFERENCE_TIME_ADJUSTMENT_HOURS))
    partial_records_for_task = current_schedule_df[current_schedule_df['task_id'] == task['task_id']]

    partially_completed_hours = 0 if partial_records_for_task.empty else \
        timedelta.total_seconds(
            ((partial_records_for_task['process_end'] - partial_records_for_task['process_start']) * partial_records_for_task['rate']).sum()
        ) / SECONDS_IN_HOURS

    hours_to_complete = (MIN_TASK_DURATION_HOURS - partially_completed_hours) / rate


    # get collectors scheduled task (employee ids are unique to each shift)
    collector_timetable = current_schedule_df[current_schedule_df['employee'] == collector['employee']]

    # check earliest time task can be picked up
    time_task_is_ready_for_process = task['earliest_processing_datetime']
    shift_start = collector['shift_start_datetime']

    if partially_completed_hours == 0:
        earliest_processing_start_given_shift_and_schedule = max(time_task_is_ready_for_process, shift_start)
    else:
        earliest_processing_start_given_shift_and_schedule = max(
            time_task_is_ready_for_process, shift_start, partial_records_for_task['process_end'].max()
        )


    # if collector_timetable is empty -> assign earliest time to task
    if collector_timetable.empty:
        collector_start = earliest_processing_start_given_shift_and_schedule
    else:
        #   get scheduled task start and end times
        collectors_scheduled_task_start = min(collector_timetable['process_start'])
        collectors_scheduled_task_end = max(collector_timetable['process_end'])

        # can this task be completed before scheduled task collectors_scheduled_task_start
        earliest_potential_end_time = \
            earliest_processing_start_given_shift_and_schedule + timedelta(hours=hours_to_complete)

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
    collector['rate'] = rate
    collector['percentage_complete'] = round(percentage_of_task_complete, 3)

    return collector
