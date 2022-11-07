import sys

from services.HW_Link_Generator_Producer import HW_Link_Generator_Producer
from services.HW_Link_Generator_Consumer import HW_Link_Generator_Consumer
from util.slack import Slack

if __name__ == '__main__':
    try:

        if sys.argv[2] == "producer":
            HW_Link_Generator_Producer()._start_crawling(sys.argv[1])
        if sys.argv[2] == "consumer":
            HW_Link_Generator_Consumer()._start_crawling(sys.argv[1])


    except Exception as e:

        print(str(e) + "Exception")
        # Slack().send_message_to_slack(GENERAL_ERROR, str(e))
