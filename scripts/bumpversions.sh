#!/bin/bash

pipenv run bumpversion --allow-dirty --commit --commit-args="--no-verify" patch
