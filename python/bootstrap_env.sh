#!/bin/sh
# ENV variables accepted:
# PYBOOTSTRAP_DIR: directory of your configs

set -e


default_bootstrap_dir="$HOME/.pybootstrap"
bootstrap_dir=${PYBOOTSTRAP_DIR:-$default_bootstrap_dir}

# if [ ! -z $PYBOOTSTRAP_DIR ]; then
#     if [ ! -d $PYBOOTSTRAP_DIR ]; then
#         echo "PYBOOTSTRAP_DIR ($PYBOOTSTRAP_DIR) is not a directory."
#         exit 1
#     elif [ ! -w $PYBOOTSTRAP_DIR ]; then
#         echo "PYBOOTSTRAP_DIR ($PYBOOTSTRAP_DIR) is not writable."
#         exit 1
#     fi
# fi

echo $bootstrap_dir
#[[ -d $bootstrap_dir ]] || mkdir -p $bootstrap_dir


project_config_dir="$( python bootstrap_env.py $@ --get-project-config)"
echo "$project_config_dir"
#$( python bootstrap_env.py $@ --get-project-config 2>> /dev/null)

#echo "$retval"


