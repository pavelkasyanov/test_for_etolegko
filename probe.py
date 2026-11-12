#!/usr/bin/env python3
"""
Console script: 10 sequential HTTP requests to a given URL,
average request time and download speed.

Usage:
    python probe.py https://example.com/big-image.png
"""

import socket
import sys
import time
from urllib.parse import urlparse

import requests

ITERATIONS = 10


def validate_url(url: str) -> None:
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        sys.exit(f"Error: only http/https supported (got: '{parsed.scheme or 'empty'}')")

    if not parsed.hostname:
        sys.exit(f"Error: no host in URL: '{url}'")

    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    try:
        socket.getaddrinfo(parsed.hostname, port, proto=socket.IPPROTO_TCP)
    except socket.gaierror as e:
        sys.exit(f"Error: cannot resolve host '{parsed.hostname}': {e}")

    print(f"URL       : {url}")
    print(f"Host      : {parsed.hostname}:{port}")
    print(f"Iterations: {ITERATIONS}")


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <URL>")
        print(f"Example: {sys.argv[0]} https://example.com/photo.jpg")
        sys.exit(1)

    url = sys.argv[1]
    validate_url(url)

    session = requests.Session()
    total_bytes = 0
    total_time = 0.0
    failures = 0
    error_samples: list[str] = []

    print("Sending requests...", end="", flush=True)

    for i in range(1, ITERATIONS + 1):
        t_start = time.monotonic()
        try:
            resp = session.get(url, stream=True, timeout=30)
            resp.raise_for_status()
            body_len = sum(len(chunk) for chunk in resp.iter_content(chunk_size=8192))
            resp.close()
        except requests.exceptions.ConnectTimeout:
            failures += 1
            error_samples.append(f"#{i}: connect timeout")
        except requests.exceptions.ReadTimeout:
            failures += 1
            error_samples.append(f"#{i}: read timeout")
        except requests.exceptions.ConnectionError as e:
            failures += 1
            error_samples.append(f"#{i}: {e}")
        except requests.exceptions.HTTPError as e:
            failures += 1
            code = e.response.status_code if e.response is not None else "?"
            error_samples.append(f"#{i}: HTTP {code}")
        except requests.exceptions.RequestException as e:
            failures += 1
            error_samples.append(f"#{i}: {e}")
        else:
            total_bytes += body_len
            total_time += time.monotonic() - t_start

    session.close()
    print(" done.")

    ok_count = ITERATIONS - failures

    print(f"\nSuccessful requests : {ok_count}/{ITERATIONS}")
    if failures:
        print(f"Failed requests     : {failures}")
        for msg in error_samples[:5]:
            print(f"  {msg}")
        if failures > 5:
            print(f"  ... and {failures - 5} more")

    if ok_count == 0:
        print("\nNo successful requests. Nothing to measure.")
        sys.exit(1)

    avg_time = total_time / ok_count
    avg_speed = total_bytes / total_time if total_time > 0 else 0

    print(f"\nAvg request time  : {avg_time:.4f} s")
    print(f"Total data        : {total_bytes} bytes")
    print(f"Avg speed         : {avg_speed:.0f} bytes/s")


if __name__ == "__main__":
    main()