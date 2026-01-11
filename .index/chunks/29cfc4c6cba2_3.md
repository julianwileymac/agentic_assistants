# Chunk: 29cfc4c6cba2_3

- source: `.venv-lab/Lib/site-packages/websocket_client-1.9.0.dist-info/METADATA`
- lines: 186-202
- chunk: 4/4

```
 if you want to confirm that a WebSocket
server is running and responds properly to a specific request.

```python
from websocket import create_connection

ws = create_connection("ws://echo.websocket.events/")
print(ws.recv())
print("Sending 'Hello, World'...")
ws.send("Hello, World")
print("Sent")
print("Receiving...")
result =  ws.recv()
print("Received '%s'" % result)
ws.close()
```
```
