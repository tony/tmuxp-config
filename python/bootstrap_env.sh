#!/bin/sh
# ENV variables accepted:
# PYBOOTSTRAP_DIR: directory of your configs

set -e

# TODO: bootstrap bootstrap, check for pip, install pystrap

# this step is needed because only shell can source into an environment.
#project_config_dir="$( python bootstrap_env.py $@ --get-project-config)"



if env | grep -q ^VIRTUAL_ENV=
then
    in_virtualenv="in_virtualenv"
fi

if env | grep -q ^PYENV_VIRTUALENV_INIT=
then
    has_pyenv_virtualenv="has_pyenv_virtualenv"
fi

if env | grep -q ^VIRTUALENVWRAPPER_VIRTUALENV=
then
    has_virtualenvwrapper="has_virtualenvwrapper"
fi

if [ -n "$in_virtualenv" ]; then echo "in virtualenv"; fi

_print_message() {
    cat <<EOF
usage: $0 [-v] [-c install_command] [project_name]
EOF
}

vflag=off
while getopts vpc: opt
do
    case "$opt" in
      v)  vflag=on;;
      p)  project_name="$OPTARG";;
      c)  install_command="$OPTARG";;
      \?)		# unknown flag
         _print_message 
          exit 1;;
    esac
done
shift `expr $OPTIND - 1`

#project_name2=${@:$OPTIND}
project_name=$@
echo $project_name
echo $install_command

# if [ ! -z $PYBOOTSTRAP_DIR ]; then
#     if [ ! -d $PYBOOTSTRAP_DIR ]; then
#         echo "PYBOOTSTRAP_DIR ($PYBOOTSTRAP_DIR) is not a directory."
#         exit 1
#     elif [ ! -w $PYBOOTSTRAP_DIR ]; then
#         echo "PYBOOTSTRAP_DIR ($PYBOOTSTRAP_DIR) is not writable."
#         exit 1
#     fi
# fi
#python bootstrap_env.py $@

#echo "$retval"


