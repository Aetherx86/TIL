from .explainer import POSIXCronEngine, CronSchedule

def explain_cron(expression: str) -> str:
    sched = POSIXCronEngine.parse(expression)
    return f"POSIX cron schedule: {expression}"

__all__ = ["POSIXCronEngine", "CronSchedule", "explain_cron"]
