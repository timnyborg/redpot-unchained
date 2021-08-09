import datetime
from typing import Optional


def academic_year(date: Optional[datetime.date] = None) -> int:
    """Get the academic year of a given date or datetime
    Academic years run 1 Aug - 31

    If not provided with a `date`, today is used
    """
    if not date:
        date = datetime.date.today()
    return date.year - int(date.month < 8)
