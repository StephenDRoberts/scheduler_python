import pandas as pd

from src.scheduler.processors.process_task import build_new_scheduled_task


class TestBuildNewScheduledTask:
    def test_should_build_new_scheduled_task(self):
        task = pd.Series({
            'task_id': 'task_1'
        })

        employee = pd.Series({
            'employee': ['employee_1'],
            'squad': 'B',
            'date': '30-01-2020',
            'shift': 'Morning',
            'shift_end_datetime': 'tomorrow',
            'employee_task_start': ['now'],
            'employee_task_end': ['later'],
            'rate': [1.0],
            'percentage_complete': [0.8],
        })

        expected = pd.DataFrame({
            'task_id': ['task_1'],
            'employee': ['employee_1'],
            'squad': 'B',
            'date': '30-01-2020',
            'shift': 'Morning',
            'shift_end_datetime': 'tomorrow',
            'process_start': ['now'],
            'process_end': ['later'],
            'rate': [1.0],
            'percentage_complete': [0.8],

        })

        result = build_new_scheduled_task(task, employee)

        pd.testing.assert_frame_equal(result, expected)
