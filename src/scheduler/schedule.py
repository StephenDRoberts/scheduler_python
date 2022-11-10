from datetime import datetime

from termcolor import colored

from src.scheduler.helpers.create_empty_dataframes import create_empty_df_from_template
from src.scheduler.processors.process_task import process_task


def schedule(tasks, collectors, preferences):
    sorted_collectors_by_shift = collectors.sort_values(by='shift_start_datetime', ascending=True)
    sorted_tasks_by_priority = tasks.sort_values(
        by=['processing_deadline', 'priority_class', 'match_id'], ascending=[True, True, True]
    )

    unique_shift_ends = sorted_collectors_by_shift['shift_end_datetime'].unique()

    # Create empty dataframes to track progress
    processed_tasks = create_empty_df_from_template(sorted_tasks_by_priority)
    partially_processed_tasks = create_empty_df_from_template(
        sorted_tasks_by_priority, {
            'percentage_complete': 0,
            'process_start': datetime.now(),
            'process_end': datetime.now(),
        }
    )
    scheduled_tasks = create_empty_df_from_template(
        sorted_tasks_by_priority, {
            'employee': '',
            'process_end': datetime.now()
        })

    for shift_index, shift_end in enumerate(unique_shift_ends):
        print(colored(f'Shift {shift_index}/{len(unique_shift_ends)} - {shift_end}', 'yellow'))

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

        # process partially processed matches as priority
        # once complete, place these games in processed_tasks and remove from partially_processed_tasks
        for index in range(len(partials_for_todays_shift)):
            partial_task = partials_for_todays_shift.iloc[index]

            # TODO need to make this a universal capacity check
            if index >= (len(employees_on_shift.index) * 3):
                continue

            state_after_process = process_task(
                partial_task, employees_on_shift, preferences, scheduled_tasks,
                processed_tasks, partially_processed_tasks
            )

            processed_tasks = state_after_process['processed_tasks']
            partially_processed_tasks = state_after_process['partially_processed_tasks']
            scheduled_tasks = state_after_process['scheduled_tasks']

        # process new tasks
        for task_index, task in tasks_excl_partially_processed.iterrows():
            state_after_process = process_task(
                task, employees_on_shift, preferences, scheduled_tasks,
                processed_tasks, partially_processed_tasks
            )

            processed_tasks = state_after_process['processed_tasks']
            partially_processed_tasks = state_after_process['partially_processed_tasks']
            scheduled_tasks = state_after_process['scheduled_tasks']

    overdue_tasks = processed_tasks[(processed_tasks['process_end'] > processed_tasks['processing_deadline'])]

    return {
        'processed_tasks': processed_tasks,
        'partially_processed_tasks': partially_processed_tasks,
        'overdue_tasks': overdue_tasks
    }
