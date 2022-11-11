from pathlib import Path


def write_to_csv(tasks_dict):
    for key in tasks_dict:
        filepath = Path(f'./output/{key}.csv')
        filepath.parent.mkdir(parents=True, exist_ok=True)
        tasks = tasks_dict[key]

        tasks.to_csv(filepath, index=False)
