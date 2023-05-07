#!/usr/bin/env bash

set -x

mypy app
black app -l 75 --check
isort --recursive --line-width 75 --check-only app
flake8
