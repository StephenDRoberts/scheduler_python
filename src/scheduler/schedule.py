from datetime import datetime

from termcolor import colored

from src.constants.constants import MAX_TASKS_PER_EMPLOYEE
from src.scheduler.helpers.create_empty_dataframes import create_empty_df_from_template
from src.scheduler.processors.process_task import process_task


def schedule(tasks, collectors, preferences):
    sorted_collectors_by_shift = collectors.sort_values(by='shift_start_datetime', ascending=True)
    sorted_tasks_by_priority = tasks.sort_values(
        by=['processing_deadline', 'priority_class', 'match_id'], ascending=[True, True, True]
    )

    unique_shift_ends = sorted_collectors_by_shift['shift_end_datetime'].unique()

    # Create empty dataframes to track progress
    processed_tasks = create_empty_df_from_template(sorted_tasks_by_priority, {
        'employee': '',
        'process_start': datetime.now(),
        'process_end': datetime.now(),
        'percentage_complete': 0,
    })
    partially_processed_tasks = create_empty_df_from_template(
        sorted_tasks_by_priority, {
            'percentage_complete': 0,
            'process_start': datetime.now(),
            'process_end': datetime.now(),
        }
    )

    for shift_index, shift_end in enumerate(unique_shift_ends):
        print(colored(f'Shift {shift_index + 1}/{len(unique_shift_ends)} - {shift_end}', 'yellow'))

        partials_for_todays_shift = partially_processed_tasks.sort_values(
            by=['processing_deadline', 'percentage_complete'],
            ascending=[True, False]
        )

        # filter for games that can be processed in this shift_end
        new_tasks_in_shift = sorted_tasks_by_priority[
            sorted_tasks_by_priority['earliest_processing_datetime'] < shift_end
            ]

        # filter out games that have already been processed
        tasks_excl_fully_processed = new_tasks_in_shift[
            ~new_tasks_in_shift.loc[:, 'task_id'].isin(processed_tasks['task_id'])]
        tasks_excl_partially_processed = tasks_excl_fully_processed[
            ~tasks_excl_fully_processed.loc[:, 'task_id'].isin(partially_processed_tasks['task_id'])]

        # filter for employees working in this shift
        employees_on_shift = sorted_collectors_by_shift[
            sorted_collectors_by_shift.loc[:, 'shift_end_datetime'] == shift_end]

        print(colored(f'Number of partial tasks in this shift: {partials_for_todays_shift["task_id"].nunique()}',
                      'green'))
        print(colored(f'Number of new tasks in this shift: {tasks_excl_partially_processed["task_id"].nunique()}',
                      'green'))
        print(colored(f'Employees on shift: {len(employees_on_shift.index)}', 'yellow'))

        capacity_used = 0
        # process partially processed matches as priority
        # once complete, place these games in processed_tasks and remove from partially_processed_tasks
        for index in range(len(partials_for_todays_shift)):
            capacity_used += 1
            partial_task = partials_for_todays_shift.iloc[index]

            # TODO need to make this a universal capacity check
            # if overcapacity for number of employee tasks - exit
            if capacity_used >= (len(employees_on_shift.index) * MAX_TASKS_PER_EMPLOYEE):
                continue

            state_after_process = process_task(
                partial_task, employees_on_shift, preferences,
                processed_tasks, partially_processed_tasks
            )

            processed_tasks = state_after_process['processed_tasks']
            partially_processed_tasks = state_after_process['partially_processed_tasks']

        # process new tasks
        for task_index, task in tasks_excl_partially_processed.iterrows():
            capacity_used += 1
            if capacity_used >= (len(employees_on_shift.index) * MAX_TASKS_PER_EMPLOYEE):
                continue
            state_after_process = process_task(
                task, employees_on_shift, preferences,
                processed_tasks, partially_processed_tasks
            )

            processed_tasks = state_after_process['processed_tasks']
            partially_processed_tasks = state_after_process['partially_processed_tasks']

    overdue_tasks = processed_tasks[(processed_tasks['process_end'] > processed_tasks['processing_deadline'])]

    processed_sorted_by_shift = processed_tasks.sort_values(by='shift_end_datetime', ascending=True)
    partials_sorted_by_shift = partially_processed_tasks.sort_values(by='shift_end_datetime', ascending=True)
    overdues_sorted_by_shift = overdue_tasks.sort_values(by='shift_end_datetime', ascending=True)

    return {
        'processed_tasks': processed_sorted_by_shift,
        'partially_processed_tasks': partials_sorted_by_shift,
        'overdue_tasks': overdues_sorted_by_shift
    }
