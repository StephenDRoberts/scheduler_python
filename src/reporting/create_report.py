def create(tasks_data):
    processed = tasks_data['processed']
    partially = tasks_data['partially']
    overdue = tasks_data['overdue']

    fully_processed_tasks = processed[processed['percentage_complete'] == 1]

    completed_tasks = fully_processed_tasks['task_id'].nunique()
    completed_matches = completed_tasks['match_id'].nunique()
    overdue_matches = overdue['match_id'].nunique()
    partially_complete_matches = partially['match_id'].nunique()

    return {
        'completed_matches': completed_matches,
        'overdue_matches': overdue_matches,
        'partially_complete_matches': partially_complete_matches,
    }
