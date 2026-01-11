# Chunk: 29cfc4c6cba2_2

- source: `.venv-lab/Lib/site-packages/websocket_client-1.9.0.dist-info/METADATA`
- lines: 117-197
- chunk: 3/4

```
you want to get better performance, install wsaccel. While
websocket-client does not depend on wsaccel, it will be used if
available. wsaccel doubles the speed of UTF8 validation and
offers a very minor 10% performance boost when masking the
payload data as part of the `send` process. Numpy used to
be a suggested performance enhancement alternative, but
[issue #687](https://github.com/websocket-client/websocket-client/issues/687)
found it didn't help.

## Examples

Many more examples are found in the
[examples documentation](https://websocket-client.readthedocs.io/en/latest/examples.html).

### Long-lived Connection

Most real-world WebSockets situations involve longer-lived connections.
The WebSocketApp `run_forever` loop will automatically try to reconnect
to an open WebSocket connection when a network
connection is lost if it is provided with:

- a `dispatcher` argument (async dispatcher like rel or pyevent)
- a non-zero `reconnect` argument (delay between disconnection and attempted reconnection)

`run_forever` provides a variety of event-based connection controls
using callbacks like `on_message` and `on_error`.
`run_forever` **does not automatically reconnect** if the server
closes the WebSocket gracefully (returning
[a standard websocket close code](https://www.rfc-editor.org/rfc/rfc6455.html#section-7.4.1)).
[This is the logic](https://github.com/websocket-client/websocket-client/pull/838#issuecomment-1228454826) behind the decision.
Customizing behavior when the server closes
the WebSocket should be handled in the `on_close` callback.
This example uses [rel](https://github.com/bubbleboy14/registeredeventlistener)
for the dispatcher to provide automatic reconnection.

```python
import websocket
import _thread
import time
import rel

def on_message(ws, message):
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    print("Opened connection")

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://api.gemini.com/v1/marketdata/BTCUSD",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)

    ws.run_forever(dispatcher=rel, reconnect=5)  # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()
```

### Short-lived Connection

This is if you want to communicate a short message and disconnect
immediately when done. For example, if you want to confirm that a WebSocket
server is running and responds properly to a specific request.

```python
from websocket import create_connection

ws = create_connection("ws://echo.websocket.events/")
print(ws.recv())
print("Sending 'Hello, World'...")
ws.send("Hello, World")
print("Sent")
```
