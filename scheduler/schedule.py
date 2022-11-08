from datetime import timedelta

import pandas as pd
from termcolor import colored

from scheduler.helpers.employee_helpers import earmark_collector

SECONDS_IN_HOURS = 60 * 60
MIN_TASK_DURATION = 4
NON_PREFERENCE_TIME_ADJUSTMENT = 1


def schedule(tasks, employees, preferences):
    sorted_employees = employees.sort_values(by='shift_start_datetime', ascending=True)
    sorted_tasks = tasks.sort_values(by='processing_deadline', ascending=True)

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
        if shift_index in range(0,3):
            print(f"Shift End Time - {shift_end}")
            # filter for games that can be processed in this shift_end
            tasks_in_shift = sorted_tasks[sorted_tasks['earliest_processing_datetime'] < shift_end]

            # filter out games that have already been processed
            tasks_excl_processed = tasks_in_shift[~tasks_in_shift.loc[:, 'match_id'].isin(processed_tasks['match_id'])]

            print("Tasks whose process can be started:")
            print(tasks_excl_processed)

            # filter for employees working in this shift
            employees_on_shift = sorted_employees[sorted_employees.loc[:, 'shift_end_datetime'] == shift_end]

            print("****COLLECTORS****")
            print(employees_on_shift)

            # TODO process partially processed matches as priority
            # process partially processed matches as priority
            # once complete, place these games in processed_tasks and remove from partially_processed_tasks




            # process tasks
            for task_index, task in tasks_excl_processed.iterrows():
                print(f'processing task index {task_index}')
                # filter out any employees who can't pick up task in their shift
                #  TODO remove so it processes everyone
                # if task_index == 0:
                competition = task['competition']
                preferred_squad = preferences[preferences['competition'] == competition]['squad'].iloc[0]

                collectors = employees_on_shift.apply(earmark_collector, axis=1, args=(
                    scheduled_tasks, task, preferred_squad
                ))


                # if no one can pick up, move to the next shift
                if (collectors.empty or collectors['percentage_complete'] == 0).all():
                    print('no collectors can pick up task, moving to next shift')
                    partial_task = task
                    partial_task['percentage_processed'] = 0.0
                    partially_processed_tasks = pd.concat([partially_processed_tasks, partial_task])
                    continue

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
                else:
                    # else add to partially processed_tasks
                    print(colored('Adding to partially complete', 'yellow'))
                    partially_processed_tasks = pd.concat([partially_processed_tasks, new_scheduled_task])


    print("COMPLETE")
    print(processed_tasks)



                    #
                    #
                    # # if no one can complete -> move to partial with 0 hours complete
                    # if available_employees.empty:
                    #     partial_task = task
                    #     partial_task['percentage_processed'] = 0.0
                    #     partially_processed_tasks = pd.concat([partially_processed_tasks, partial_task])
                    #     continue
                    #
                    #
                    # # TODO is there a partition function for this?
                    # # filter or sort employees that have expertise in the competition
                    # preferred_employees = available_employees[available_employees['squad'] == preferred_squad]
                    # not_preferred_employees = available_employees[available_employees['squad'] != preferred_squad]
                    #
                    # #  TODO order who can pick up task the soonest
                    # # sort remaining employees by who can pick the task up first
                    #
                    #
                    # # assign task
                    # assigned_employee = preferred_employees.iloc[0] if not preferred_employees.empty else \
                    #     not_preferred_employees.iloc[0]
                    #
                    # # calculate whether full task can be completed
                    # assigned_task_times = calculate_pickup_and_completion_time(
                    #     assigned_employee, scheduled_tasks, task, preferred_squad
                    # )
                    # task_start = assigned_task_times['start']
                    # task_end = assigned_task_times['end']
                    # task_duration = timedelta.total_seconds(task_end - task_start) / SECONDS_IN_HOURS
                    #
                    #
                    # task_completion_percentage = calculate_percentage_of_task_complete(
                    #     task_duration, assigned_employee.equals(preferred_employees.iloc[0], )
                    # )
                    #
                    # # if complete -> move to processed & log times.
                    # if task_completion_percentage == 1:
                    #     completed_task = task
                    #     completed_task['percentage_processed'] = task_completion_percentage
                    #     completed_task['processed_by'] = assigned_employee
                    #     completed_task['process_start'] = task_start
                    #     completed_task['process_end'] = task_end
                    #     completed_task['']
                    # # if not -> move to partial & calculate hours complete
                    # else:
                    #     partial_task = task
                    #     partial_task['percentage_processed'] = task_completion_percentage
                    #     partial_task['processed_by'] = assigned_employee
                    #     partial_task['process_start'] = task_start
                    #     partially_processed_tasks = pd.concat([partially_processed_tasks, partial_task])


def calculate_percentage_of_task_complete(time_complete, preference_employee):
    if preference_employee:
        return time_complete / MIN_TASK_DURATION
    else:
        return time_complete / (MIN_TASK_DURATION + NON_PREFERENCE_TIME_ADJUSTMENT)
