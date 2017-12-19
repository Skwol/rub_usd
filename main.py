import os
import pandas as pd
from itertools import permutations


WEEKDAYS = {
    0: 'monday',
    1: 'tuesday',
    2: 'wednesday',
    3: 'thursday',
    4: 'friday',
    5: 'saturday',
    6: 'sunday',
}
INITIAL_MONEY = 1000000.  # initial amount of money (rub)

WEEKDAY = 'weekday'
PRICE = 'price'
DATE = 'date'


def get_data_frame_from_csv():
    """Get csv file from the current directory and tronsform do DataFrame object. """
    path_to_dataset = os.path.abspath(__file__).replace('main.py', 'export.csv')
    frame = pd.read_csv(path_to_dataset, delimiter=',')
    return frame


def clean_up_df(frame):
    """Remove redundant columns and rename them. """
    frame = frame.loc[:, ['my_date', 'my_value']]
    frame.columns = DATE, PRICE
    return frame


def parse_dates_and_add_weekday(frame):
    """Converting string to datetime and adding weekday column."""
    frame.date = pd.to_datetime(frame[DATE], format='%d.%m.%Y')
    frame[WEEKDAY] = df.date.dt.dayofweek
    frame[WEEKDAY].astype(int, inplace=True)
    return frame


def get_result_dict(frame):
    """Creating dictionary with results. """
    results_dict = {}
    frame.set_index(frame.date, inplace=True)
    frame.drop(DATE, axis=1, inplace=True)
    for buy_day, sell_day in permutations(frame[WEEKDAY].unique(), r=2):
        #  iterating through every possible days combination and creating DataFrame for each
        current_frame = frame[(frame[WEEKDAY] == buy_day) | (frame[WEEKDAY] == sell_day)]
        current_frame = remove_repeted_days(frame=current_frame, initial_day=sell_day)
        if len(current_frame) < 100:
            continue  # filter out days, when we have few data
        money_after_trades = get_money_result_for_selected_days(current_frame, buy_day)
        results_dict[money_after_trades] = (WEEKDAYS[buy_day], WEEKDAYS[sell_day])
    return results_dict


def remove_repeted_days(frame, initial_day):
    """Removing rows, where days are the same nearby, last entry should be the selling day. """
    sell_day = initial_day
    dates_to_remove = []
    previous_date = None
    for date, row in frame.iterrows():
        if row[WEEKDAY] == initial_day:
            # remove secondary entry (current) if it is sell, remove first entry (previous) if buy
            dates_to_remove.append(date if initial_day == sell_day else previous_date)
        else:
            initial_day = row[WEEKDAY]
        previous_date = date
    if sell_day != frame.iloc[-1:][WEEKDAY][0]:
        #  last day should be the day we sell
        dates_to_remove.append(frame.iloc[-1:].index[0])
    return frame.drop(dates_to_remove, axis=0)


def get_money_result_for_selected_days(frame, buy_day):
    """Perform trades. """
    money = INITIAL_MONEY
    for date, row in frame.iterrows():
        if row[WEEKDAY] == buy_day:
            money = money / row[PRICE]
        else:
            money = money * row[PRICE]
    return money


def transform_results_to_dataframe(results):
    """Convert result dictionary to DataFrame object. """
    columns = ['buy day', 'sell day', 'profit, %']
    transformed = {col: [] for col in columns}
    for money, (buy_day, sell_day) in results.iteritems():
        transformed['profit, %'].append((money - INITIAL_MONEY) / INITIAL_MONEY * 100)
        transformed['buy day'].append(buy_day)
        transformed['sell day'].append(sell_day)
    results_frame = pd.DataFrame.from_dict(transformed)[columns]
    results_frame.sort_values('profit, %', inplace=True, ascending=False)
    return results_frame

if __name__ == '__main__':
    df = get_data_frame_from_csv()
    df = clean_up_df(df)
    df = parse_dates_and_add_weekday(df)
    results_dict = get_result_dict(df)
    result_df = transform_results_to_dataframe(results_dict)
    result_df.to_excel('profit.xlsx', index=False)
