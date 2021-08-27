#!/bin/bash

cd fluidly-structlog
pipenv run bumpversion --allow-dirty --commit --commit-args="--no-verify" patch
