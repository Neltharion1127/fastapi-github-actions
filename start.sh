#!/bin/sh
set -e

# Start nginx (daemonizes by default on Debian)
nginx -t
nginx

# Start FastAPI behind nginx
exec uvicorn app.main:app --host 127.0.0.1 --port 8000