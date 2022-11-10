def create(processed, partially, overdue):
    total_processed_tasks = len(processed[processed['percentage_complete'] == 1])
    total_overdue_tasks = overdue.count()
    total_partial_tasks_outstanding = partially.count()

