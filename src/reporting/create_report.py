def create(tasks_data):
    processed = tasks_data['processed_tasks']
    partially = tasks_data['partially_processed_tasks']
    overdue = tasks_data['overdue_tasks']

    fully_processed_tasks = processed[processed['percentage_complete'] == 1]
    counts = fully_processed_tasks['match_id'].value_counts().rename_axis('match_id').reset_index(name='counts')
    fully_processed_tasks = fully_processed_tasks.merge(counts, on=['match_id'])
    fully_processed_tasks = fully_processed_tasks[fully_processed_tasks['counts'] == 2]

    completed_matches = fully_processed_tasks['match_id'].nunique()
    overdue_matches = overdue['match_id'].nunique()
    partially_complete_matches = partially['match_id'].nunique()

    return {
        'completed_matches': completed_matches,
        'overdue_matches': overdue_matches,
        'partially_complete_matches': partially_complete_matches,
    }
