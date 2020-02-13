"""
Gunicorn configuration file for loading up SPBM.
"""
import os
import multiprocessing
from glob import glob

debug = int(os.environ.get("SPBM_DEBUG", default=0))

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() + 1
worker_class = "meinheld.gmeinheld.MeinheldWorker" if not debug else "sync"
reload_engine = "inotify"
reload = True if debug else False
reload_extra_files = glob("../**/*.py", recursive=True) if debug else []
