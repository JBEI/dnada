#!/usr/bin/env bash

set -x

mypy app
black app -l 88 --check
isort --recursive --line-width 88 --check-only app
flake8
