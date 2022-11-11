import pandas as pd


# TODO defensive coding around bad csv formats
def parse(filepath):
    data = pd.read_csv(filepath)
    df = pd.DataFrame(data)
    return df
