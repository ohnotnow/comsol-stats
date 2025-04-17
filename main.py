#!/usr/bin/env python3
"""
This script parses a Comsol license log file and extracts key fields, using scattered date markers
so that each event gets a full date+time datetime. It then creates an Excel workbook with several sheets containing:
  - All parsed log events (with full datetime)
  - Aggregated feature usage counts
  - Aggregated user usage counts
  - Usage counts by hour
  - Daily unique user counts
  - Summary user stats

Additionally, it produces visualizations using Seaborn:
  - Bar chart for feature usage
  - Line plot for usage by hour
  - Bar chart for top active users

Usage:
    python parse_comsol_log_updated.py comsol62.log
"""

import re
import sys
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Regex to parse event lines (unchanged)
def parse_log_line(line):
    pattern = r'^(?P<timestamp>\d{2}:\d{2}:\d{2}).*?\s(?P<direction>IN|OUT):\s"(?P<feature>[^\"]+)"\s+(?P<user>\S+)'
    match = re.search(pattern, line)
    if match:
        return match.groupdict()
    return None

# Regex to detect scattered date lines (e.g. "Time: Mon Mar 10 2025 16:26:55 GMT Standard Time")
DATE_LINE_RE = re.compile(
    r'Time:\s+(?P<date_str>\w{3} \w{3} \d{1,2} \d{4})\s+'  
    r'(?P<time_str>\d{2}:\d{2}:\d{2})'
)


def main(log_file):
    events = []
    current_date = None

    with open(log_file, 'r') as f:
        for line in f:
            # 1) Look for explicit date markers and update current context date
            date_match = DATE_LINE_RE.search(line)
            if date_match:
                # Parse into a date object
                dt = datetime.datetime.strptime(
                    f"{date_match.group('date_str')} {date_match.group('time_str')}",
                    "%a %b %d %Y %H:%M:%S"
                )
                current_date = dt.date()
                continue

            # 2) Parse normal event lines
            parsed = parse_log_line(line)
            if parsed:
                # Attach the most recent date context
                if current_date is None:
                    # If no date seen yet, you may choose to set a default or skip
                    raise RuntimeError("No date context found before first event. Ensure the log includes a date marker.")
                parsed['date'] = current_date
                events.append(parsed)

    if not events:
        print("No events found in the log file. Please check the file format.")
        return

    # Build DataFrame
    df = pd.DataFrame(events)

    # Combine date and timestamp into full datetime
    df['datetime'] = pd.to_datetime(
        df['date'].astype(str) + ' ' + df['timestamp'],
        format='%Y-%m-%d %H:%M:%S'
    )
    # Extract hour and ensure date column matches
    df['hour'] = df['datetime'].dt.hour
    df['date'] = df['datetime'].dt.date

    # Daily unique-user stats
    daily_users = (
        df.groupby('date')['user']
          .nunique()
          .reset_index(name='unique_user_count')
    )
    avg_users = daily_users['unique_user_count'].mean()
    max_users = daily_users['unique_user_count'].max()
    user_stats = pd.DataFrame({
        'metric': ['average_users_per_day', 'max_users_per_day'],
        'value': [avg_users, max_users]
    })

    # Aggregate usage tables
    feature_usage = df['feature'].value_counts().rename_axis('feature').reset_index(name='count')
    user_usage = df['user'].value_counts().rename_axis('user').reset_index(name='count')
    usage_by_hour = df['hour'].value_counts().sort_index().reset_index(name='count')

    # Write to Excel
    excel_file = 'comsol_license_analysis.xlsx'
    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='LogEvents', index=False)
        feature_usage.to_excel(writer, sheet_name='FeatureUsage', index=False)
        user_usage.to_excel(writer, sheet_name='UserUsage', index=False)
        usage_by_hour.to_excel(writer, sheet_name='UsageByHour', index=False)
        daily_users.to_excel(writer, sheet_name='DailyUserCounts', index=False)
        user_stats.to_excel(writer, sheet_name='UserStats', index=False)
    print(f"Excel file '{excel_file}' has been created with parsed log data and aggregated tables.")

    # Visualizations
    sns.set(style="whitegrid")
    # Feature usage bar
    plt.figure(figsize=(10,6))
    sns.barplot(data=feature_usage, x='feature', y='count')
    plt.title('Feature Usage Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('feature_usage.png')
    plt.show()

    # Usage across hours
    plt.figure(figsize=(10,6))
    sns.lineplot(data=usage_by_hour, x='hour', y='count', marker='o')
    plt.title('Usage Across Hours of the Day')
    plt.tight_layout()
    plt.savefig('usage_by_hour.png')
    plt.show()

    # Top 10 users
    top_users = user_usage.head(10)
    plt.figure(figsize=(10,6))
    sns.barplot(data=top_users, x='user', y='count')
    plt.title('Top 10 Active Users')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('user_usage.png')
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: uv run main.py <log_file>")
    else:
        main(sys.argv[1])

