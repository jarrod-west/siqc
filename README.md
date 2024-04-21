# siqc
Scheduled In-Queue Callbacks

## Requirements

* python3
* global pipenv

## Running

Update the file at deploy/.env

TODO: init.sh

1. pipenv install
1. pipenv shell
1. python -m deploy.deploy


## Notes

* Deleting flow stack requires unassigning number

## TODO

* Teardown script
  * Remove user from RP
  * Undo associations DONE
* Set some attributes on contact that make it clear what it is
* Update default agent whisper
* ruff format and mypy pre-push hooks DONE
* No unused (except with leading underscore) DONE
* Proper docstrings