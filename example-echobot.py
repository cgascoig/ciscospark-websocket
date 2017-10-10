#!/usr/bin/env python
from ciscosparkwebsocket import CiscoSpark
import logging
import os
import sys

spark=None

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s  [%(levelname)s]  [%(module)s.%(name)s.%(funcName)s]:%(lineno)s %(message)s')
    
def on_message(message):
    spark.spark.messages.create(roomId=message.roomId, text=message.text)

if __name__ == '__main__':
    token=os.getenv('SPARK_TOKEN')
    if token is None:
        print('SPARK_TOKEN environment variable not set, exiting')
        sys.exit(-1)
    
    setup_logging()
    
    logging.info('echobot starting')
    
    spark = CiscoSpark(access_token=token, on_message=on_message)
    spark.run()
