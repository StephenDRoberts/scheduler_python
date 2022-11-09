import sys

from termcolor import colored

from formatters.format_competitions import format_competitions
from formatters.format_matches import format_matches_to_tasks
from formatters.format_preferences import format_preferences
from formatters.format_priorities import format_priorities
from formatters.format_schedule import format_schedule
from formatters.transform import transform
from joiners.preferences_joiner import hydrate_preferences
from parser.parse_csv import parse
from joiners.match_info_joiner import combine_match_info
from scheduler.schedule import schedule


def main():
    #  TODO defensive coding when file corrupt
    try:
        raw_priorities = parse('./resources/priorities.csv')
        raw_matches = parse('./resources/matches.csv')
        raw_competitions = parse('./resources/competitions.csv')
        raw_schedule = parse('./resources/schedule.csv')
        raw_preferences = parse('./resources/preferences.csv')
    except FileNotFoundError as file_not_found:
        print(f"File not found: {file_not_found}")
        sys.exit(1)

    formatted_priorities_df = transform(raw_priorities, format_priorities)
    tasks_df = transform(raw_matches, format_matches_to_tasks)
    formatted_competitions_df = transform(raw_competitions, format_competitions)
    formatted_schedule_df = transform(raw_schedule, format_schedule)
    formatted_preferences_df = transform(raw_preferences, format_preferences)

    combined_match_info = combine_match_info(tasks_df, formatted_competitions_df, formatted_priorities_df)
    complete_preferences = hydrate_preferences(formatted_preferences_df, formatted_competitions_df)

    schedule(combined_match_info, formatted_schedule_df, complete_preferences)

    print(colored("Process complete!", 'green'))


if __name__ == '__main__':
    main()
