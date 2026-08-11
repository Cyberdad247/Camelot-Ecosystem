# -*- coding: utf-8 -*-
"""Driver: run `notebooklm login` and press ENTER when a trigger flag appears.

The browser session is completed by a human; once they signal completion, we
create the trigger file and this driver writes ENTER to the CLI so it saves
the session. Fully detached from the parent shell.
"""
import os
import subprocess
import sys
import threading
import time

NLM = r"C:\Users\vizio\CAMELOT_OS\.venv\Scripts\notebooklm.exe"
TRIGGER = r"C:\Users\vizio\CAMELOT_OS\_tmp\nlm_enter.flag"
LOG = r"C:\Users\vizio\CAMELOT_OS\_tmp\nlm_login.log"

if os.path.exists(TRIGGER):
    os.remove(TRIGGER)

logf = open(LOG, "ab", buffering=0)
p = subprocess.Popen(
    [NLM, "login"],
    stdin=subprocess.PIPE,
    stdout=logf,
    stderr=subprocess.STDOUT,
    cwd=r"C:\Users\vizio\CAMELOT_OS",
)


def _waiter() -> None:
    while p.poll() is None and not os.path.exists(TRIGGER):
        time.sleep(2)
    if p.poll() is None:
        try:
            # The CLI asks TWO prompts in sequence: (1) "Press ENTER when
            # logged in", then (2) "Save authentication anyway? [y/N]".
            # Answer both from the pipe buffer: blank line for (1), "y" for (2).
            p.stdin.write(b"\ny\n")
            p.stdin.flush()
            time.sleep(5)
            p.stdin.close()
        except Exception:
            pass


threading.Thread(target=_waiter, daemon=True).start()
p.wait()
logf.close()
sys.exit(p.returncode)
