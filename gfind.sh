#!/bin/bash          

# gfind.sh -- script to retrieve all groups for a specific user
#             - returns the groups in CSV form
# invoke by running: ./gfind.sh [UTLN], returns a string concatenated by commas
#                    of all groups that user is in
#                    e.g. ./gfind.sh aplume01 -> "grade170,grade20,ta170,ta11"

if [ $# -gt 0 ]; then

        groups $1 | cut -d: -f2 | cut -d ' ' -f2- | sed 's/ /,/g'

else
        echo "Arguments missing"
fi
