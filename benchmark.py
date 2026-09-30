import time
import urllib.request
import json
import subprocess
import os
import signal
import sys

def run_benchmark():
    # Start the server
    server_process = subprocess.Popen(['python3', 'server.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(1) # wait for server to start

    try:
        url = 'http://localhost:8000/api/ingest'
        data = json.dumps({'raw_text': 'This is a sample text for benchmarking performance.'}).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

        # Warmup
        for _ in range(2):
            urllib.request.urlopen(req)

        # Benchmark
        start = time.time()
        num_requests = 10
        for _ in range(num_requests):
            urllib.request.urlopen(req)
        end = time.time()

        print(f"Total time for {num_requests} requests: {end - start:.4f}s")
        print(f"Average time per request: {(end - start)/num_requests:.4f}s")
    finally:
        os.kill(server_process.pid, signal.SIGTERM)
        server_process.wait()

if __name__ == '__main__':
    run_benchmark()
