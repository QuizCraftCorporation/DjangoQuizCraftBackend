#!/bin/sh

celery -A app worker -l info --concurrency 4 -E