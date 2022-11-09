from datetime import datetime

import pandas as pd
from termcolor import colored

from scheduler.helpers.create_empty_dataframes import create_empty_df_from_template


def test_should_return_empty_df_with_original_column_types():
    original_df = pd.DataFrame({
        'name': ['steve'],
        'id': [123],
        'date': [datetime.now()]
    })

    result = create_empty_df_from_template(original_df)

    pd.testing.assert_series_equal(result.dtypes, original_df.dtypes)
    assert list(result.columns) == list(original_df.columns)
    assert result.empty

def test_should_return_empty_df_with_new_column_types():
    original_df = pd.DataFrame({
        'name': ['steve'],
        'id': [123],
        'date': [datetime.now()]
    })

    new_series_dict = {
        'on': [True]
    }

    new_series = pd.Series({'on': bool})
    expected_dtypes = pd.concat([original_df.dtypes, new_series])
    expected_columns = ['name', 'id', 'date', 'on']


    result = create_empty_df_from_template(original_df, new_series_dict)

    pd.testing.assert_series_equal(result.dtypes, expected_dtypes)
    assert list(result.columns) == expected_columns
    assert result.empty