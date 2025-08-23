# Gunicorn config (Uvicorn workers)

import multiprocessing
workers = max(2, multiprocessing.cpu_count() * 2 + 1)
worker_class = "uvicorn.workers.UvicornWorker"
bind = "0.0.0.0:5555"
timeout = 60
graceful_timeout = 30
keepalive = 5

loglevel = "info"
accesslog = "-"
errorlog = "-"
