#!/bin/bash

EXIT_CODE=0
CHANGED_FILES=$(git diff --name-only origin/master)

CHANGED_DIRS=$(
    for FILE in $CHANGED_FILES
    do
        if [[ $FILE == fluidly-* ]]
        then
            echo "$FILE" | cut -d "/" -f1
        fi
    done | sort | uniq
)

for DIR in $CHANGED_DIRS
do
    if [[ ! $CHANGED_FILES =~ "$DIR/setup.py" ]]
    then
        echo "Need to bump version in $DIR/setup.py with scripts/bumpversions.sh script"
        EXIT_CODE=1
    fi

    if [[ ! $CHANGED_FILES =~ "$DIR/.bumpversion.cfg" ]]
    then
        echo "Need to bump version in $DIR/.bumpversion.cfg with scripts/bumpversions.sh script"
        EXIT_CODE=1
    fi
done

exit $EXIT_CODE
