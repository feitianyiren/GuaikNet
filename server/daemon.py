#-*- coding:UTF-8 -*-
import logging
import os,sys

def daemon(path):
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        logging.error("fork #1 failed: %d (%s)" % (e.errno, e.strerror))
        sys.exit(1)

    os.chdir(path)
    os.setsid()
    os.umask(0)

    try:
        pid = os.fork()
        if pid > 0:
            logging.info("GuaikNet PID %d" % pid)
            sys.exit(0)
    except OSError, e:
        logging.error("fork #2 failed: %d (%s)" % (e.errno, e.strerror))
        sys.exit(1)
