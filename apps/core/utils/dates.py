from datetime import date


def academic_year(_date: date = None):
    """ Get the academic year of a given date or datetime
        Academic years run 1 Aug - 31

        If not provided with a _date, today is used
    """
    if not _date:
        _date = date.today()
    return _date.year - 1 if _date.month < 9 else _date.year
