import calendar
import datetime
from dataclasses import dataclass
from typing import List, Optional, Set, Tuple

@dataclass
class CronSchedule:
    minutes: Set[int]
    hours: Set[int]
    days_of_month: Set[int]
    months: Set[int]
    days_of_week: Set[int]
    raw_expression: str
    is_dom_wildcard: bool
    is_dow_wildcard: bool

class POSIXCronEngine:
    """
    IEEE Std 1003.1 (POSIX) Cron parser and recurrence engine.
    Supports step expressions, ranges, lists, and POSIX day-of-month /
    day-of-week union disjunction rules with leap year compensation.
    """
    MONTH_MAP = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
                 "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}
    DOW_MAP = {"SUN": 0, "MON": 1, "TUE": 2, "WED": 3, "THU": 4, "FRI": 5, "SAT": 6}

    @classmethod
    def _parse_field(cls, field_str: str, min_val: int, max_val: int, alias_map: Optional[dict] = None) -> Set[int]:
        s = field_str.strip().upper()
        if alias_map:
            for k, v in alias_map.items():
                s = s.replace(k, str(v))

        result: Set[int] = set()
        sub_tokens = s.split(",")
        for tok in sub_tokens:
            if tok == "*":
                result.update(range(min_val, max_val + 1))
            elif tok.startswith("*/"):
                step = int(tok[2:])
                result.update(range(min_val, max_val + 1, step))
            elif "-" in tok:
                if "/" in tok:
                    range_part, step_part = tok.split("/")
                    step = int(step_part)
                else:
                    range_part = tok
                    step = 1
                start_str, end_str = range_part.split("-")
                start = int(start_str)
                end = int(end_str)
                result.update(range(start, end + 1, step))
            else:
                val = int(tok)
                # In cron, 7 is often treated as Sunday (0)
                if max_val == 6 and val == 7:
                    val = 0
                if min_val <= val <= max_val:
                    result.add(val)
                else:
                    raise ValueError(f"Value {val} out of bounds [{min_val}, {max_val}]")
        return result

    @classmethod
    def parse(cls, expression: str) -> CronSchedule:
        parts = expression.strip().split()
        if len(parts) != 5:
            raise ValueError("Cron expression must have exactly 5 fields: minute hour dom month dow")

        dom_wildcard = (parts[2] == "*")
        dow_wildcard = (parts[4] == "*")

        minutes = cls._parse_field(parts[0], 0, 59)
        hours = cls._parse_field(parts[1], 0, 23)
        doms = cls._parse_field(parts[2], 1, 31)
        months = cls._parse_field(parts[3], 1, 12, cls.MONTH_MAP)
        dows = cls._parse_field(parts[4], 0, 6, cls.DOW_MAP)

        return CronSchedule(
            minutes=minutes,
            hours=hours,
            days_of_month=doms,
            months=months,
            days_of_week=dows,
            raw_expression=expression,
            is_dom_wildcard=dom_wildcard,
            is_dow_wildcard=dow_wildcard,
        )

    @classmethod
    def next_occurrences(cls, schedule: CronSchedule, start_dt: datetime.datetime, count: int = 5) -> List[datetime.datetime]:
        """Calculates exact subsequent firing timestamps according to POSIX specification."""
        curr = start_dt.replace(second=0, microsecond=0) + datetime.timedelta(minutes=1)
        occurrences: List[datetime.datetime] = []

        # Advance minute by minute with hierarchical skip
        while len(occurrences) < count:
            if curr.month not in schedule.months:
                # Advance to first day of next month
                if curr.month == 12:
                    curr = datetime.datetime(curr.year + 1, 1, 1, 0, 0, tzinfo=curr.tzinfo)
                else:
                    curr = datetime.datetime(curr.year, curr.month + 1, 1, 0, 0, tzinfo=curr.tzinfo)
                continue

            # POSIX Day-of-month and Day-of-week rule:
            # If both are non-wildcard, match if EITHER matches (union)
            # If one is wildcard, match the non-wildcard one
            dow = curr.weekday()
            # Python weekday: Mon=0 .. Sun=6 -> Cron: Sun=0, Mon=1 .. Sat=6
            cron_dow = (dow + 1) % 7
            max_days_in_month = calendar.monthrange(curr.year, curr.month)[1]
            if curr.day > max_days_in_month:
                curr = datetime.datetime(curr.year, curr.month + 1, 1, 0, 0, tzinfo=curr.tzinfo)
                continue

            dom_match = curr.day in schedule.days_of_month
            dow_match = cron_dow in schedule.days_of_week

            if not schedule.is_dom_wildcard and not schedule.is_dow_wildcard:
                day_match = dom_match or dow_match
            elif not schedule.is_dom_wildcard:
                day_match = dom_match
            elif not schedule.is_dow_wildcard:
                day_match = dow_match
            else:
                day_match = True

            if not day_match:
                curr = (curr + datetime.timedelta(days=1)).replace(hour=0, minute=0)
                continue

            if curr.hour not in schedule.hours:
                curr = (curr + datetime.timedelta(hours=1)).replace(minute=0)
                continue

            if curr.minute not in schedule.minutes:
                curr += datetime.timedelta(minutes=1)
                continue

            occurrences.append(curr)
            curr += datetime.timedelta(minutes=1)

        return occurrences
