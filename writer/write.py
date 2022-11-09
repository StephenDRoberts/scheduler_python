from pathlib import Path


def write_to_csv(tasks, name):
    filepath = Path(f'./output/{name}.csv')
    filepath.parent.mkdir(parents=True, exist_ok=True)
    tasks.to_csv(filepath, index=False)
