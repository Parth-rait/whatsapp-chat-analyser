import pandas as pd
import re


def preprocess(data):
    pattern = r'\[(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}:\d{2} [APap][Mm])\] (.+?): (.*)'
    messages = []
    dates = []
    users = []

    for line in data.split('\n'):
        match = re.match(pattern, line)
        if match:
            date = match.group(1)
            time = match.group(2)
            user = match.group(3).strip()
            message = match.group(4).strip()
            messages.append(message)
            dates.append(f"{date}, {time}")
            users.append(user)
        else:
            # Append to last message if it's multiline
            if messages:
                messages[-1] += ' ' + line.strip()

    df = pd.DataFrame({'user': users, 'message': messages,
                       'datetime': pd.to_datetime(dates, format='%d/%m/%y, %I:%M:%S %p', errors='coerce')})
    df = df.dropna(subset=['datetime'])  # Drop rows with unparsable dates

    # Add additional time-based columns
    df['only_date'] = df['datetime'].dt.date
    df['year'] = df['datetime'].dt.year
    df['month'] = df['datetime'].dt.month_name()
    df['month_num'] = df['datetime'].dt.month
    df['day'] = df['datetime'].dt.day
    df['day_name'] = df['datetime'].dt.day_name()
    df['hour'] = df['datetime'].dt.hour
    df['minute'] = df['datetime'].dt.minute

    # Define period column for heatmap
    df['period'] = df['hour'].apply(lambda x: f"{x}-{x + 1 if x < 23 else 0}")

    return df
