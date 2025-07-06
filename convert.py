import sys
from importlib import reload
from workflow3 import Workflow, ICON_CLOCK
import logging
import time
import datetime
LOGGER: logging.Logger
reload(sys)

def show_now(__workflow__: Workflow):
    timestamp13 = int(time.time() * 1000)
    timestamp10 = int(time.time())

    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    __workflow__.add_item(title=str(timestamp13), arg=str(timestamp13), subtitle="13位时间戳", icon=ICON_CLOCK, valid=True)
    __workflow__.add_item(title=str(timestamp10), arg=str(timestamp10), subtitle="10位时间戳", icon=ICON_CLOCK, valid=True)
    __workflow__.add_item(title=formatted_time, arg=formatted_time, subtitle="时间",  icon=ICON_CLOCK, valid=True)

def convert_timestamp(__workflow__: Workflow, timestamp: int, seconds: bool):
    dt = datetime.datetime.fromtimestamp(timestamp)
    formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
    __workflow__.add_item(title=formatted_time, arg=formatted_time, subtitle="时间戳:"+( "秒" if seconds else "毫秒"), valid=True)


def default_output(__workflow__: Workflow):
    __workflow__.add_item(title="等待....", subtitle="输入now或10|13位时间戳")


def converter(__workflow__: Workflow):
    query = __workflow__.args[0]

    if query == 'now':
        show_now(__workflow__)
    elif query.isdigit():
        if len(query) == 10 or len(query) == 13:
            timestamp = int(query)
            if len(query) == 13:
                timestamp = timestamp / 1000
            convert_timestamp(__workflow__, int(timestamp), len(query) == 10)
        else:
            default_output(__workflow__)
    elif len(__workflow__.args) == 2:
        LOGGER.info(f"query: {__workflow__.args}")
        try:
            query = f"{__workflow__.args[0]} {__workflow__.args[1]}"
            dt = datetime.datetime.strptime(query, "%Y-%m-%d %H:%M:%S")
            timestamp10 = int(dt.timestamp())
            timestamp13 = int(dt.timestamp() * 1000)

            __workflow__.add_item(title=str(timestamp10), arg=str(timestamp10), subtitle="10位时间戳", icon=ICON_CLOCK, valid=True)
            __workflow__.add_item(title=str(timestamp13), arg=str(timestamp13), subtitle="13位时间戳", icon=ICON_CLOCK, valid=True)
        except ValueError:
            default_output(__workflow__)
    else:
        default_output(__workflow__)

def main(__workflow__: Workflow):
    if len(__workflow__.args) > 0:
        converter(__workflow__)
    else:
        default_output(__workflow__)

    __workflow__.send_feedback()


if __name__ == '__main__':
    wf = Workflow()
    LOGGER = wf.logger()
    LOGGER.info('Starting convert workflow'+ sys.argv[1])
    main(wf)
