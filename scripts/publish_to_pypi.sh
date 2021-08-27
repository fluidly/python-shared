#!/bin/bash

DIRS=$(find . -type d -name "fluidly-*")

for DIR in $DIRS
do
    cd $DIR
    pipenv run python setup.py sdist bdist_wheel
    pipenv run twine upload --skip-existing dist/*
    cd -
done
