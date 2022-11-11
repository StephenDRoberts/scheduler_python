import pandas as pd

from src.parser.parse_csv import parse


class TestParse:
    csv = 'id,name,bool\n' \
          '123,steve,True'

    def test_should_parse_csv_to_df(self):
        expected = pd.DataFrame({
            'id': [123],
            'name': ['steve'],
            'bool': [True]
        })

        result = parse('test_data')
        # TODO mock call to read_csv
        # pd.testing.assert_frame_equal(result, expected)