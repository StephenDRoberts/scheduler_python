from formatters.format_competitions import format_competitions
from formatters.format_matches import format_matches_to_tasks
from formatters.format_preferences import format_preferences
from formatters.format_priorities import format_priorities
from formatters.format_schedule import format_schedule
from formatters.transform import transform
from parser.parse_csv import parse
from joiners.match_info_joiner import combine_match_info
from scheduler.schedule import schedule


def main():
    raw_priorities = parse('./resources/priorities.csv')
    formatted_priorities_df = transform(raw_priorities, format_priorities)

    raw_matches = parse('./resources/matches.csv')
    tasks_df = transform(raw_matches, format_matches_to_tasks)

    raw_competitions = parse('./resources/competitions.csv')
    formatted_competitions_df = transform(raw_competitions, format_competitions)

    raw_schedule = parse('./resources/schedule.csv')
    formatted_schedule_df = transform(raw_schedule, format_schedule)

    raw_preferences = parse('./resources/preferences.csv')
    preferences_dict = transform(raw_preferences, format_preferences)

    combined_match_info = combine_match_info(tasks_df, formatted_competitions_df, formatted_priorities_df)
    #  TODO delete underlying function
    # combined_schedule_info = combine_schedule_info(formatted_schedule_df, formatted_preferences_df)

    # print(combined_match_info)
    print(formatted_schedule_df)

    schedule(combined_match_info, formatted_schedule_df, preferences_dict)

if __name__ == '__main__':
    main()
