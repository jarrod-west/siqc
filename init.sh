#!/bin/sh

set -e pipefail

pipenv install
pre-commit install --hook-type pre-push