#!/usr/bin/env python3

import sys
import subprocess
import signal
import time
import os

DEFAULT_NUM_INSTANCES = 3

def usage():
    print(f"Usage: {sys.argv[0]} <number_of_instances>")
    print(f"  <number_instances>: The number of Flask instances to spawn (1 or more). Default is {DEFAULT_NUM_INSTANCES}.")

def is_valid_num(num) -> bool:
    return num.isdigit() and int(num) > 0

def start_flask_instance(i, port) -> subprocess.Popen:
    env = os.environ.copy()
    env["INSTANCE"] = str(i)
    proc = subprocess.Popen(
        ["poetry", "run", "flask", "--app", "server", "run", "--host", "0.0.0.0", "--port", str(port)],
        env=env
    )
    print(f"  PID: {proc.pid}")
    return proc

def kill_flask_instances(procs: list):
    if len(procs) == 0:
        print("No Flask instances to kill.")
        return
    
    print("Killing Flask instances...")
    for proc in procs:
        if proc.poll() is None:
            print(f"Process with PID {proc.pid} is running. Attempting to terminate.")
            proc.terminate()
            time.sleep(1)
            if proc.poll() is None:
                print(f"Process with PID {proc.pid} did not terminate. Sending SIGKILL.")
                proc.kill()
            else:
                print(f"Process with PID {proc.pid} terminated.")
        else:
            print(f"Process with PID {proc.pid} is not running.")
    print("Flask instances killed.")



def main():
    num_instances = int(sys.argv[1]) if len(sys.argv) > 1 and is_valid_num(sys.argv[1]) else DEFAULT_NUM_INSTANCES
    if not is_valid_num(str(num_instances)):
        usage()
        sys.exit(1)

    procs = []

    def handle_exit(signum, frame):
        kill_flask_instances(procs)
        sys.exit(0)

    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGQUIT):
        signal.signal(sig, handle_exit)

    print(f"Spawning {num_instances} Flask instances...")
    
    start_port = 5000
    ports = []
    for i in range(num_instances):
        port = start_port
        print(f"Starting Flask instance on port {port}...")
        ports.append(port)
        start_port += 1

    for i in range(len(ports)):
        procs.append(start_flask_instance(i, ports[i]))
        time.sleep(0.1)

    print("Flask instances started. PIDs:", [p.pid for p in procs])

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        handle_exit(None, None)

if __name__ == "__main__":
    main()
