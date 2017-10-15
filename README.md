# ciscospark-websocket

This module can be used to build a bot for Cisco Spark that only uses outbound connections (useful if you want to run the bot from behind a firewall where inbound webhook connections are not possible). Two types of outbound connections are used - a websocket connection for the bot to receive notifications of events and REST API calls to the Spark service to retrieve messages, etc.

## Getting Started
### Prerequisites
 - Python's async features (async/await) are used, so requires Python 3.6 (tested with Python 3.6.2)
 - [pipenv](https://docs.pipenv.org) is used to manage requirements. As long as you have pipenv installed you should just need to run `pipenv install` to install all the dependencies.
 - If you want to install the dependencies manually, you should only need the following packages from PyPI:
   - `uuid`
   - `ciscosparkapi`
   - `websockets`
 
## Usage
### Example

An example of how this can be used is included in `example-echobot.py` but the simplest example is:

``` python
from ciscosparkwebsocket import CiscoSpark

token = '<REPLACE WITH YOUR TOKEN FROM developer.ciscospark.com>'

def on_message(message):
  # TODO: handle the message received by the bot. Below just echos the message back to the sender
  spark.spark.messages.create(roomId=message.roomId, text=message.text)
  
spark = CiscoSpark(token=token, on_message=on_message)
spark.run()

```

### Notes

 - CiscoSpark.run() starts the event loop so will not return until the bot exits. 
 - CiscoSpark.spark is an instance of [ciscosparkapi](http://ciscosparkapi.readthedocs.io/en/latest/) - a simple, lightweight, scalable Python API wrapper for the Cisco Spark APIs and can be used to respond to messages, etc. (In the example above it is used to create the reply message).

## Acknowledgements

 - The Cisco Spark websocket API is not publicy documented, so this is based on the NodeJS implementation [here](https://github.com/marchfederico/ciscospark-websocket-events). 
