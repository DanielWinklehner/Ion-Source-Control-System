# Ion Source Control System

## Arduino Error Codes
'ERR0' => Undefined error (does not fall into any of the other 9 categories).
'ERR1' => Asking a precision that's too high (> 6).
'ERR2' => Asking for something that would return more than 128 bytes.
'ERR3' => Invalid number of channels.
'ERR4' => Querying for a channel that does not exist.
'ERR5' => ...
'ERR6' => ...
'ERR7' => ...
...


## Libraries to Install


## Killing the server.

```bash
ps aux | grep DummyServer.py | head -n 1 | grep -o '[a-z]  [0-9]*' | grep -o '\([0-9]*\) \{0\}' | xargs kill -9
```

```bash
ps aux | grep DummyServer.py | head -n 1 | grep -o '[a-z]  [0-9]*' | grep -o '\([0-9]*\) \{0\}' | xargs kill -9 && python DummyServer.py
```