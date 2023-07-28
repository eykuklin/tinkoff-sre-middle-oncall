import datetime
import time
import signal
import sys
from loguru import logger
from ProcOncall import ProcOncall
from prometheus_client import start_http_server, Gauge


ONCALL_SHIFTS = Gauge('duty', "List of shifts in Oncall", ["team", "role", "user"])


def signal_handler(sig, frame):
    logger.warning("Ctrl+C pressed. Quitting...")
    sys.exit(0)


def get_metrics(oncall_instance:ProcOncall):
    # Get teams
    teams = oncall_instance.get_team_list()
    now_time = datetime.datetime.now()
    now_time = int(now_time.timestamp())
    for team in teams:
        # Get events
        events = oncall_instance.get_team_events(team)
        for event in events:
            # Check only shifts in current data
            if event['start'] < now_time < event['end']:
                metric = 1 if event['role'] == 'primary' else 0
                ONCALL_SHIFTS.labels(role=event['role'], user=event['full_name'], team=team).set(metric)


def main():
    # Catch Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    # Start up the server to expose the metrics.
    try:
        start_http_server(8002)
    except Exception as e:
        logger.error("Failed to start web server. Quit...")
        raise
    else:
        logger.success("Web server started...")

    # Create instance
    oncall_instance = ProcOncall()
    # Get cookie and token
    oncall_instance.get_credentials()
    # Scrape metrics
    while True:
        get_metrics(oncall_instance)
        time.sleep(10)


if __name__ == '__main__':
    main()
