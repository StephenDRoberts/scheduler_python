import sys
from datetime import datetime

from termcolor import colored

from src.formatters.format_competitions import format_competitions
from src.formatters.format_matches import format_matches_to_tasks
from src.formatters.format_preferences import format_preferences
from src.formatters.format_priorities import format_priorities
from src.formatters.format_schedule import format_schedule
from src.formatters.transform import transform
from src.joiners.match_info_joiner import combine_match_info
from src.joiners.preferences_joiner import hydrate_preferences
from src.parser.parse_csv import parse
from src.reporting.create_report import create
from src.scheduler.schedule import schedule
from src.writer.write import write_to_csv


def main():
    process_start = datetime.now()
    # Extract
    #  TODO defensive coding when file corrupt
    try:
        print("Parsing CSVs")
        raw_priorities = parse('./resources/priorities.csv')
        raw_matches = parse('./resources/matches.csv')
        raw_competitions = parse('./resources/competitions.csv')
        raw_schedule = parse('./resources/schedule.csv')
        raw_preferences = parse('./resources/preferences.csv')
    except FileNotFoundError as file_not_found:
        print(f"File not found: {file_not_found}")
        sys.exit(1)

    # Transform
    print("Transforming")
    formatted_priorities_df = transform(raw_priorities, format_priorities)
    formatted_tasks_df = transform(raw_matches, format_matches_to_tasks)
    formatted_competitions_df = transform(raw_competitions, format_competitions)
    formatted_schedule_df = transform(raw_schedule, format_schedule)
    formatted_preferences_df = transform(raw_preferences, format_preferences)

    # Join
    combined_match_info = combine_match_info(formatted_tasks_df, formatted_competitions_df, formatted_priorities_df)
    complete_preferences = hydrate_preferences(formatted_preferences_df, formatted_competitions_df)

    # Run task
    print("Running scheduler")
    tasks_data = schedule(combined_match_info, formatted_schedule_df, complete_preferences)

    # Load
    write_to_csv(tasks_data)

    process_end = datetime.now()

    print('*****************')
    print("Process complete!")
    print('*****************')
    print(f'The scheduler took {process_end - process_start} to run')


    print(colored("The current schedule can be found under /output/processed_tasks.csv", 'green'))
    print(colored("Overdue tasks can be found under /output/overdue_tasks.csv", 'red'))

    # Report
    report = create(tasks_data)
    print(colored(f'There were {report["completed_matches"]} fully completed matches', 'green'))
    print(colored(f'- of which {report["overdue_matches"]} were overdue', 'red'))
    print(colored(f'In addition there are {report["partially_complete_matches"]} partially complete', 'yellow'))


if __name__ == '__main__':
    main()
