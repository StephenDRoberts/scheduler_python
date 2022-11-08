from datetime import timedelta

import pandas as pd

from scheduler.helpers.employee_helpers import is_available_for_task, calculate_pickup_and_completion_time

SECONDS_IN_HOURS = 60 * 60
MIN_TASK_DURATION = 4
NON_PREFERENCE_TIME_ADJUSTMENT = 1


def schedule(tasks, employees, preferences):
    sorted_employees = employees.sort_values(by='shift_start_datetime', ascending=True)
    sorted_tasks = tasks.sort_values(by='processing_deadline', ascending=True)

    unique_shift_ends = sorted_employees['shift_end_datetime'].unique()

    processed_tasks = pd.DataFrame(
        columns=sorted_tasks.columns.tolist() + ['processed_by', 'process_start', 'process_end'])
    partially_processed_tasks = pd.DataFrame(
        columns=sorted_tasks.columns.tolist() + ['processed_by', 'process_start', 'percentage_processed'])
    employee_timetable = pd.DataFrame(columns=['employee', 'match_id', 'team', 'process_start', 'employee_process_end'])

    for shift_index, shift_end in enumerate(unique_shift_ends):
        if shift_index == 2:
            # TODO
            # process partially processed matches as priority
            # once complete, place these games in processed_tasks and remove from partially_processed_tasks

            # filter for games that can be processed in this shift_end
            tasks_in_shift = sorted_tasks[sorted_tasks['earliest_processing_datetime'] < shift_end]

            # filter out games that have already been processed
            tasks_excl_processed = tasks_in_shift[~tasks_in_shift.loc[:, 'match_id'].isin(processed_tasks['match_id'])]

            # filter for employees working in this shift
            employees_on_shift = sorted_employees[sorted_employees.loc[:, 'shift_start_datetime'] == shift_end]

            # process tasks
            for task_index, task in tasks_excl_processed.iterrows():
                # filter out any employees who can't pick up task in their shift
                #  TODO remove so it processes everyone
                if task_index == 0:
                    competition = task['competition']
                    preferred_squad = preferences[preferences['competition'] == competition]['squad'].iloc[0]

                    available_employees = employees_on_shift[
                        employees_on_shift.apply(is_available_for_task, axis=1, args=(
                            employee_timetable, task, preferred_squad
                        ))]






                    # if no one can complete -> move to partial with 0 hours complete
                    if available_employees.empty:
                        partial_task = task
                        partial_task['percentage_processed'] = 0.0
                        partially_processed_tasks = pd.concat([partially_processed_tasks, partial_task])
                        continue


                    # TODO is there a partition function for this?
                    # filter or sort employees that have expertise in the competition
                    preferred_employees = available_employees[available_employees['squad'] == preferred_squad]
                    not_preferred_employees = available_employees[available_employees['squad'] != preferred_squad]

                    #  TODO order who can pick up task the soonest
                    # sort remaining employees by who can pick the task up first


                    # assign task
                    assigned_employee = preferred_employees.iloc[0] if not preferred_employees.empty else \
                        not_preferred_employees.iloc[0]

                    # calculate whether full task can be completed
                    assigned_task_times = calculate_pickup_and_completion_time(
                        assigned_employee, employee_timetable, task, preferred_squad
                    )
                    task_start = assigned_task_times['start']
                    task_end = assigned_task_times['end']
                    task_duration = timedelta.total_seconds(task_end - task_start) / SECONDS_IN_HOURS


                    task_completion_percentage = calculate_percentage_of_task_complete(
                        task_duration, assigned_employee.equals(preferred_employees.iloc[0], )
                    )

                    # if complete -> move to processed & log times.
                    if task_completion_percentage == 1:
                        completed_task = task
                        completed_task['percentage_processed'] = task_completion_percentage
                        completed_task['processed_by'] = assigned_employee
                        completed_task['process_start'] = task_start
                        completed_task['process_end'] = task_end
                        completed_task['']
                    # if not -> move to partial & calculate hours complete
                    else:
                        partial_task = task
                        partial_task['percentage_processed'] = task_completion_percentage
                        partial_task['processed_by'] = assigned_employee
                        partial_task['process_start'] = task_start
                        partially_processed_tasks = pd.concat([partially_processed_tasks, partial_task])



def calculate_percentage_of_task_complete(time_complete, preference_employee):
    if preference_employee:
        return time_complete / MIN_TASK_DURATION
    else:
        return time_complete / (MIN_TASK_DURATION + NON_PREFERENCE_TIME_ADJUSTMENT)
