# TODO DELETE!!!
from parser.parse_csv import parse


def test_full_main_not_changed():
    total_matches = parse('../../resources/matches.csv')
    overdue = parse('../../output/overdue.csv')
    prev_overdue = parse('../../output/ss/overdue.csv')
    processed = parse('../../output/processed.csv')
    prev_processed = parse('../../output/ss/processed.csv')

    # processed_matches = processed['match_id']
    overdue_matches = overdue['match_id'].nunique()
    overdue_tasks = overdue['task_id'].nunique()
    processed_matches = processed['match_id'].nunique()
    processed_tasks = processed['task_id'].nunique()


    prev_overdue_matches = prev_overdue['match_id'].nunique()
    prev_overdue_tasks = prev_overdue['task_id'].nunique()
    prev_processed_matches = prev_processed['match_id'].nunique()
    prev_processed_tasks = prev_processed['task_id'].nunique()

    print(f'{overdue_matches} / {overdue_tasks} of {processed_matches} processed')
    print(f'{prev_overdue_matches} / {prev_overdue_tasks} of {prev_processed_matches} processed')

    assert overdue_matches == prev_overdue_matches
    assert overdue_tasks == prev_overdue_tasks
    assert processed_matches == prev_processed_matches

def test_small_main_not_changed():
    total_matches = parse('../../resources/matches.csv')
    overdue = parse('../../output/overdue.csv')
    prev_overdue = parse('../../output/test1/overdue.csv')

    processed = parse('../../output/processed.csv')
    prev_processed = parse('../../output/test1/processed.csv')


    overdue_matches = overdue['match_id'].nunique()
    overdue_tasks = overdue['task_id'].nunique()
    processed_matches = processed['match_id'].nunique()

    prev_overdue_matches = prev_overdue['match_id'].nunique()
    prev_overdue_tasks = prev_overdue['task_id'].nunique()
    prev_processed_matches = prev_processed['match_id'].nunique()

    print(f'{overdue_matches} / {overdue_tasks} of {processed_matches} processed')
    print(f'{prev_overdue_matches} / {prev_overdue_tasks} of {prev_processed_matches} processed')

    assert overdue_matches == prev_overdue_matches
    assert overdue_tasks == prev_overdue_tasks
    assert processed_matches == prev_processed_matches
