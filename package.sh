#!/bin/sh

set -e

if [ -z "$1" ]; then
  echo "Deployment output not provided"
  exit 1
fi

pipenv requirements > src/requirements.txt

docker run \
  -it \
  --rm \
  -v ${PWD}:/src \
  -e CI_WORKSPACE=/src \
  -e GLOB_IGNORE=export,deploy,docs*.pyc,__pycache__,.mypy_cache \
  -e ARTIFACT_NAME="$1" \
  3mcloud/lambda-packager:python-latest
