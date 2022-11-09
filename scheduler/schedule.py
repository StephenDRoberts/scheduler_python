from datetime import timedelta

import pandas as pd
from termcolor import colored
from pathlib import Path

from scheduler.helpers.employee_helpers import earmark_collector

SECONDS_IN_HOURS = 60 * 60
MIN_TASK_DURATION = 4
NON_PREFERENCE_TIME_ADJUSTMENT = 1


def schedule(tasks, employees, preferences):
    sorted_employees = employees.sort_values(by='shift_start_datetime', ascending=True)
    sorted_tasks = tasks.sort_values(by=['processing_deadline', 'priority_class', 'match_id'], ascending=[True, True, True])

    unique_shift_ends = sorted_employees['shift_end_datetime'].unique()

    processed_tasks = sorted_tasks.copy(deep=False)
    processed_tasks.astype(sorted_tasks.dtypes.to_dict())
    processed_tasks = processed_tasks.iloc[0:0]

    partially_processed_tasks = sorted_tasks.copy(deep=False)
    partially_processed_tasks.astype(sorted_tasks.dtypes.to_dict())
    partially_processed_tasks = partially_processed_tasks.iloc[0:0]

    scheduled_tasks = sorted_tasks.copy(deep=False)
    scheduled_tasks.astype(sorted_tasks.dtypes.to_dict())
    scheduled_tasks = scheduled_tasks.iloc[0:0]
    scheduled_tasks['employee'] = ''

    for shift_index, shift_end in enumerate(unique_shift_ends):
        partials_for_todays_shift = partially_processed_tasks



        if shift_index in range(0, 4):
            print(colored(f"Shift End Time - {shift_end}"), "orange")
            # filter for games that can be processed in this shift_end
            tasks_in_shift = sorted_tasks[sorted_tasks['earliest_processing_datetime'] < shift_end]

            # filter out games that have already been processed
            tasks_excl_processed = tasks_in_shift[~tasks_in_shift.loc[:, 'match_id'].isin(processed_tasks['match_id'])]

            # print("Tasks whose process can be started:")
            # print(tasks_excl_processed)

            # filter for employees working in this shift
            employees_on_shift = sorted_employees[sorted_employees.loc[:, 'shift_end_datetime'] == shift_end]

            # print("****COLLECTORS****")
            # print(employees_on_shift)

            # TODO process partially processed matches as priority
            # process partially processed matches as priority
            # once complete, place these games in processed_tasks and remove from partially_processed_tasks
            for partial_task_index, partial_task in partials_for_todays_shift.iterrows():
                print(colored(f'processing partials - Total: {len(partials_for_todays_shift.index)}', 'yellow'))
                state_after_process = process_task(
                    partial_task, partial_task_index, employees_on_shift, preferences, scheduled_tasks,
                    processed_tasks, partially_processed_tasks
                )

                processed_tasks = state_after_process['processed_tasks']
                partially_processed_tasks = state_after_process['partially_processed_tasks']
                scheduled_tasks = state_after_process['scheduled_tasks']



            # process tasks
            for task_index, task in tasks_excl_processed.iterrows():
                print(colored(f'processing mains - Total: {len(tasks_excl_processed.index)}', 'green'))
                # if task_index == 2:
                state_after_process = process_task(
                    task, task_index, employees_on_shift, preferences, scheduled_tasks,
                    processed_tasks, partially_processed_tasks
                )

                processed_tasks = state_after_process['processed_tasks']
                partially_processed_tasks = state_after_process['partially_processed_tasks']
                scheduled_tasks = state_after_process['scheduled_tasks']


    processed_output_filepath = Path('./output/processed.csv')
    processed_output_filepath.parent.mkdir(parents=True, exist_ok=True)
    processed_tasks.to_csv(processed_output_filepath, index=False)

    partially_processed_output_filepath = Path('./output/partial.csv')
    partially_processed_output_filepath.parent.mkdir(parents=True, exist_ok=True)
    partially_processed_tasks.to_csv(partially_processed_output_filepath, index=False)

    overdue_output_filepath = Path('./output/overdue.csv')
    overdue_output_filepath.parent.mkdir(parents=True, exist_ok=True)
    overdue_tasks = processed_tasks[(processed_tasks['process_end'] > processed_tasks['processing_deadline'])]
    overdue_tasks.to_csv(overdue_output_filepath, index=False)


    # print("COMPLETE")
    # print(colored(processed_tasks, 'green'))
    # print("PARTIAL")
    # print(colored(partially_processed_tasks, 'yellow'))
    # print("OVERDUE")
    # overdue = processed_tasks[(processed_tasks['process_end'] > processed_tasks['processing_deadline'])]
    # print(colored(overdue, 'red'))


def process_task(task, task_index, employees_on_shift, preferences, scheduled_tasks, processed_tasks,
                 partially_processed_tasks):
    # filter out any employees who can't pick up task in their shift



    competition = task['competition']
    preferred_squad = preferences[preferences['competition'] == competition]['squad'].iloc[0]

    collectors = employees_on_shift.apply(earmark_collector, axis=1, args=(
        scheduled_tasks, task, preferred_squad
    ))

    # if no one can pick up, move to the next shift
    if (collectors.empty or collectors['percentage_complete'] == 0).all():
        # print('no collectors can pick up task, moving to next shift')
        partial_task = pd.DataFrame([task])
        partial_task['employee'] = ''
        partial_task['process_start'] = ''
        partial_task['process_end'] = ''
        partial_task['percentage_complete'] = 0.0
        partially_processed_tasks = pd.concat([partially_processed_tasks, partial_task])
        return {
            'processed_tasks': processed_tasks,
            'partially_processed_tasks': partially_processed_tasks,
            'scheduled_tasks': scheduled_tasks
        }
    else:

        # otherwise, sort collectors by who can complete the complete the most, then by earliest
        sorted_collectors = collectors.sort_values(
            ['percentage_complete', 'collector_end'], ascending=[False, True]
        )

        assigned_collector = sorted_collectors.iloc[0]

        # add task information to scheduled tasks
        new_scheduled_task = pd.DataFrame([task])
        new_scheduled_task['employee'] = assigned_collector['employee']
        new_scheduled_task['process_start'] = assigned_collector['collector_start']
        new_scheduled_task['process_end'] = assigned_collector['collector_end']
        new_scheduled_task['percentage_complete'] = assigned_collector['percentage_complete']

        scheduled_tasks = pd.concat([scheduled_tasks, new_scheduled_task])

        # if complete -> add to processed_tasks
        if assigned_collector['percentage_complete'] == 1:
            processed_tasks = pd.concat([processed_tasks, new_scheduled_task])
            partially_processed_tasks = partially_processed_tasks.drop(
                partially_processed_tasks[partially_processed_tasks['match_id'] == task['match_id']].index
            )

        else:
            # else add to partially processed_tasks
            # print(colored('Adding to partially complete', 'yellow'))
            # print(colored(new_scheduled_task, 'yellow'))
            partially_processed_tasks = pd.concat([partially_processed_tasks, new_scheduled_task])
            # this is added to processed so we'll have 2 entries for any partially processed records.
            # we'll need to allow for multiple records in the reporting
            #  TODO make sure duplicate match_ids is handled in the reporting
            processed_tasks = pd.concat([processed_tasks, new_scheduled_task])

        return {
            'processed_tasks': processed_tasks,
            'partially_processed_tasks': partially_processed_tasks,
            'scheduled_tasks': scheduled_tasks
        }


def calculate_percentage_of_task_complete(time_complete, preference_employee):
    if preference_employee:
        return time_complete / MIN_TASK_DURATION
    else:
        return time_complete / (MIN_TASK_DURATION + NON_PREFERENCE_TIME_ADJUSTMENT)
