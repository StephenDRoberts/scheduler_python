import pandas as pd

from scheduler.helpers.employee_helpers import is_available_for_task


def schedule(tasks, employees, preferences):
    sorted_employees = employees.sort_values(by='shift_start_datetime', ascending=True)
    sorted_tasks = tasks.sort_values(by='processing_deadline', ascending=True)

    unique_shift_ends = sorted_employees['shift_end_datetime'].unique()
    print(sorted_employees.head())

    processed_tasks = pd.DataFrame(
        columns=sorted_tasks.columns.tolist() + ['processed_by', 'process_start', 'process_end'])
    partially_processed_tasks = pd.DataFrame(
        columns=sorted_tasks.columns.tolist() + ['processed_by', 'process_start', 'hours_processed'])
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

                    available_employees = employees_on_shift[
                        employees_on_shift.apply(is_available_for_task, axis=1, args=(employee_timetable, task))]


                    # if no one can complete -> move to partial with 0 hours complete
                    if available_employees.empty:
                        pd.concat([partially_processed_tasks, task])
                        continue

                    # fetch preferred squad
                    preferred_squad = preferences[preferences['competition'] == task['competition']]['squad'].iloc[0]

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




                # if so -> move to processed & log times. if not -> move to partial & calculate hours complete
