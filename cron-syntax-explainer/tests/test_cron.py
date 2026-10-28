import datetime
import unittest
from cron_explainer.explainer import POSIXCronEngine

class TestCronEngine(unittest.TestCase):
    def test_step_and_range_parsing(self):
        sched = POSIXCronEngine.parse("*/15 9-17 * * 1-5")
        self.assertEqual(sched.minutes, {0, 15, 30, 45})
        self.assertEqual(sched.hours, set(range(9, 18)))
        self.assertEqual(sched.days_of_week, {1, 2, 3, 4, 5})

    def test_next_occurrences_calculation(self):
        sched = POSIXCronEngine.parse("30 4 1 * *")  # 4:30 AM on 1st of every month
        start = datetime.datetime(2026, 1, 1, 5, 0)
        next_runs = POSIXCronEngine.next_occurrences(sched, start, count=2)
        self.assertEqual(next_runs[0], datetime.datetime(2026, 2, 1, 4, 30))
        self.assertEqual(next_runs[1], datetime.datetime(2026, 3, 1, 4, 30))

    def test_posix_dow_dom_union(self):
        # When both DOM and DOW are specified, fire on either
        sched = POSIXCronEngine.parse("0 0 1 * 1")  # 1st of month OR Mondays
        start = datetime.datetime(2026, 6, 1, 0, 1)  # June 1, 2026 is a Monday
        next_runs = POSIXCronEngine.next_occurrences(sched, start, count=2)
        # June 8, 2026 is the next Monday
        self.assertEqual(next_runs[0], datetime.datetime(2026, 6, 8, 0, 0))

if __name__ == "__main__":
    unittest.main()
