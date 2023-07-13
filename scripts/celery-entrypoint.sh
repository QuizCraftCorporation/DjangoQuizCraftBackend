#!/bin/sh

watchmedo auto-restart --directory=./ --pattern=*.py --recursive -- celery -A app worker --concurrency=1 --loglevel=INFO