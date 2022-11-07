import pandas as pd


def parse(filepath):
    data = pd.read_csv(filepath)
    df = pd.DataFrame(data)
    return df
