import pandas as pd
import numpy as np
from datetime import timedelta

schedule_columns = {
    'Quantity': 'quantity',
    'Shift': 'shift',
    'Date': 'date',
    'Squad': 'squad'
}

MORNING_SHIFT_START_TIME = "10:00"
NIGHT_SHIFT_START_TIME = "18:00"
SHIFT_DURATION_IN_HOURS = 8


def format_schedule(df):
    df = df.rename(columns=schedule_columns)

    shift_start_time = np.where(df['shift'] == 'Morning', MORNING_SHIFT_START_TIME, NIGHT_SHIFT_START_TIME)
    df['shift_start_datetime'] = pd.to_datetime(df['date'] + shift_start_time, format='%Y-%m-%d%H:%M')
    df['shift_end_datetime'] = pd.to_datetime(df['date'] + shift_start_time, format='%Y-%m-%d%H:%M') + timedelta(
        hours=SHIFT_DURATION_IN_HOURS)

    staff_schedule_df = df.copy(deep=False)
    staff_schedule_df.astype(df.dtypes.to_dict())
    staff_schedule_df = staff_schedule_df.iloc[0:0]

    for index, row in df.iterrows():
        for staff_number in range(row['quantity']):
            # TODO - is this new object creation needed? feels like it's slowing the process down
            data = pd.DataFrame([row])
            data['employee'] = f'employee-{row["squad"]}-{row["date"]}-{staff_number + 1}'

            staff_schedule_df = pd.concat([staff_schedule_df, data], ignore_index=True)

    return staff_schedule_df
