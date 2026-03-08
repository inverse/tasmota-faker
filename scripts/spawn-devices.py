#!/usr/bin/env python3

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

DEFAULT_NUM_INSTANCES = 3
PID_FILE = Path(".server-pids")


def usage():
    print(f"Usage: {sys.argv[0]} <number_of_instances>")
    print(
        f"  <number_instances>: The number of Flask instances to spawn (1 or more). Default is {DEFAULT_NUM_INSTANCES}."
    )


def is_valid_num(num) -> bool:
    return num.isdigit() and int(num) > 0


def read_pid_file() -> list:
    if not PID_FILE.exists():
        return []
    with PID_FILE.open() as f:
        return [line.strip() for line in f if line.strip()]


def start_flask_instance(i, port) -> subprocess.Popen:
    env = os.environ.copy()
    env["INSTANCE"] = str(i)
    proc = subprocess.Popen(
        [
            "poetry",
            "run",
            "flask",
            "--app",
            "server",
            "run",
            "--host",
            "0.0.0.0",
            "--port",
            str(port),
        ],
        env=env,
    )
    print(f"  PID: {proc.pid}")
    with PID_FILE.open("a") as f:
        f.write(f"{proc.pid}\n")
    return proc


def kill_flask_instances(procs: list):
    if len(procs) == 0:
        print("No Flask instances to kill.")
        return

    print("Killing Flask instances...")
    for proc in procs:
        pid = str(proc.pid)
        killed = False
        if proc.poll() is None:
            print(f"Process with PID {pid} is running. Attempting to terminate.")
            proc.terminate()
            time.sleep(1)
            if proc.poll() is None:
                print(f"Process with PID {pid} did not terminate. Sending SIGKILL.")
                proc.kill()
                time.sleep(1)
                if proc.poll() is None:
                    print(f"Process with PID {pid} could not be killed.")
                else:
                    print(f"Process with PID {pid} killed.")
                    killed = True
            else:
                print(f"Process with PID {pid} terminated.")
                killed = True
        else:
            print(f"Process with PID {pid} is not running.")
            killed = True

        if killed and PID_FILE.exists():
            pids = read_pid_file()
            pids = [p for p in pids if p != pid]
            if pids:
                with PID_FILE.open("w") as f:
                    for p in pids:
                        f.write(f"{p}\n")
            else:
                PID_FILE.unlink()
    print("Flask instances killed.")


def main():
    if PID_FILE.exists():
        with PID_FILE.open() as f:
            pids = [line.strip() for line in f if line.strip()]
        if len(pids) > 0:
            print(
                f"WARNING: {PID_FILE} is not empty. Previous server PIDs may still be running:"
            )
            for pid in pids:
                print(f"  PID: {pid}")
            print("Ensure they are stopped and remove this file after")
            sys.exit(0)

    num_instances = (
        int(sys.argv[1])
        if len(sys.argv) > 1 and is_valid_num(sys.argv[1])
        else DEFAULT_NUM_INSTANCES
    )
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
