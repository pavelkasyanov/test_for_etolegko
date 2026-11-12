# HTTP Probe

A console utility that fires **10 sequential HTTP requests** to a given URL, waits for each response to complete, then reports the average request time and download speed.

## Requirements

- Python 3.8+
- [`requests`](https://pypi.org/project/requests/)

```bash
pip install requests
```

# Usage
```bash
python probe.py <URL>
```

# Output
- Avg request time  : 0.8134 s
- Total data        : 1073741824 bytes
- Avg speed         : 1319900000 bytes/s

