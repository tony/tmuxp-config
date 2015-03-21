#!/bin/sh
# ENV variables accepted:
# PYBOOTSTRAP_DIR: directory of your configs

set -e

# this step is needed because only shell can source into an environment.
project_config_dir="$( python bootstrap_env.py $@ --get-project-config)"

# if [ ! -z $PYBOOTSTRAP_DIR ]; then
#     if [ ! -d $PYBOOTSTRAP_DIR ]; then
#         echo "PYBOOTSTRAP_DIR ($PYBOOTSTRAP_DIR) is not a directory."
#         exit 1
#     elif [ ! -w $PYBOOTSTRAP_DIR ]; then
#         echo "PYBOOTSTRAP_DIR ($PYBOOTSTRAP_DIR) is not writable."
#         exit 1
#     fi
# fi
python bootstrap_env.py $@

#echo "$retval"


