import pandas as pd

def transform(raw_data, formatter):
    df = pd.DataFrame(raw_data)
    return formatter(df)
