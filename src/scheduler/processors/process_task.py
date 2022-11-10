import pandas as pd

from src.scheduler.helpers.employee_helpers import task_planner


def process_task(task, employees_on_shift, preferences, scheduled_tasks,
                 processed_tasks, partially_processed_tasks):
    competition = task['competition']
    preferred_squad = preferences[preferences['competition'] == competition]['squad'].iloc[0]

    planned_employees = employees_on_shift.apply(task_planner, axis=1, args=(scheduled_tasks, task, preferred_squad))

    # if no one can pick up, add task to partials, move to the next shift
    if (planned_employees['percentage_complete'] == 0).all():
        partial_task = pd.DataFrame([task])

        partially_processed_tasks = pd.concat([partially_processed_tasks, partial_task])

        return {
            'processed_tasks': processed_tasks,
            'partially_processed_tasks': partially_processed_tasks,
            'scheduled_tasks': scheduled_tasks
        }
    else:
        # otherwise, sort planned_employees by who can complete the most, then by earliest
        sorted_employees = planned_employees.sort_values(
            ['percentage_complete', 'employee_task_end'], ascending=[False, True]
        )

        assigned_employee = sorted_employees.iloc[0]

        # add task information to scheduled tasks
        new_scheduled_task = build_new_scheduled_task(task, assigned_employee)
        scheduled_tasks = pd.concat([scheduled_tasks, new_scheduled_task])

        # if complete -> add to processed_tasks
        if assigned_employee['percentage_complete'] == 1:
            processed_tasks = pd.concat([processed_tasks, new_scheduled_task])

            partially_processed_tasks = partially_processed_tasks[
                ~partially_processed_tasks.loc[:, 'task_id'].isin(processed_tasks['task_id'])]

        else:
            partially_processed_tasks = pd.concat([partially_processed_tasks, new_scheduled_task])
            # this is added to processed so we'll have 2 entries for any partially processed records for timetable purposes.
            processed_tasks = pd.concat([processed_tasks, new_scheduled_task])

        return {
            'processed_tasks': processed_tasks,
            'partially_processed_tasks': partially_processed_tasks,
            'scheduled_tasks': scheduled_tasks
        }


def build_new_scheduled_task(task, assigned_employee):
    new_scheduled_task = pd.DataFrame([task])
    new_scheduled_task['employee'] = assigned_employee['employee']
    new_scheduled_task['squad'] = assigned_employee['squad']
    new_scheduled_task['date'] = assigned_employee['date']
    new_scheduled_task['shift'] = assigned_employee['shift']
    new_scheduled_task['shift_end_datetime'] = assigned_employee['shift_end_datetime']
    new_scheduled_task['process_start'] = assigned_employee['employee_task_start']
    new_scheduled_task['process_end'] = assigned_employee['employee_task_end']
    new_scheduled_task['rate'] = assigned_employee['rate']
    new_scheduled_task['percentage_complete'] = assigned_employee['percentage_complete']

    return new_scheduled_task
