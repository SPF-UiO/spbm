"""
Gunicorn configuration file for loading up SPBM.
"""
import os
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "meinheld.gmeinheld.MeinheldWorker"
reload = True if os.environ.get("SPBM_DEBUG", default=0) else False
