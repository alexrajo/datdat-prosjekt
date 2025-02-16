import datetime


def get_weekday_year_from_string(date_string: str):
    date = datetime.datetime.strptime(date_string, '%Y-%m-%d')
    week_number = date.isocalendar()[1]
    weekday_number = date.isoweekday()
    year = int(date.strftime('%Y'))
    return weekday_number, week_number, year

def get_date_from_weekinfo(year: int, week: int, weekday: int):
    date_string = "{}-W{}-{}".format(year, week, weekday)
    return datetime.datetime.strptime(date_string, "%Y-W%W-%w").date()


if __name__ == "__main__":
    command = input()
    arguments = command.split(" ")

    if arguments[0] == "date_to_weekday_year":
        date_string = arguments[1]
        print(get_weekday_year_from_string(date_string))
