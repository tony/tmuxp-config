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


if command -v virtualenv
then
    has_virtualenv="has_virtualenv"
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

# user outside of virtualenv without virtualenv installed.
if [ ! -n "$in_virtualenv" ] && [ ! -n "$has_virtualenv" ]; then
    cat <<EOF
You must install virtualenv, see:
https://virtualenv.pypa.io/en/latest/installation.html
EOF
    exit 1
fi



# user queried project name, but no virtualenvwrapper



_print_message() {
    cat <<EOF
usage: $0 [-v] [-m manager] [-c install_command] [project_name]

        -m  (optional) virtualenv|pyenv-virtualenv|virtualenvwrapper
            will do the best to autodetect your virtual environment manager.

        -c  commands (if any) to install / prepare python environment
            e.g. -c "python setup.py install", "pip install -e .",
            "pip install -r requirements.txt"

        project_name can be any valid directory name.
EOF
}

vflag=off
OPTIND=1
while getopts "hvp:m:c:" opt
do
    case "$opt" in
      h)
          _print_message
          exit 0
          ;;
      v)  vflag=on;;
      p)  project_name="$OPTARG";;
      m)  
          manager="$OPTARG"
          if [ "$manager" != "virtualenv" ] && [ "$manager" != "virtualenv" ] && [ "$manager" != "virtualenv" ]; then
              echo "Incorrect manager, must specify virtualenv, virtualenvwrapper or pyenv-virtualenv"
              exit 1
          fi
          ;;
      c)  install_command="$OPTARG";;
      \?)		# unknown flag
         _print_message 
          exit 1;;
    esac
done
shift `expr $OPTIND - 1`

#project_name2=${@:$OPTIND}
#project_name=$@
echo "all: $@"
echo "project_name: $project_name"
echo "install_command: $install_command"
echo "manager: $manager"

_detect_manager() {
    echo "hi"
}

if [ -z "$manager" ]; then  # no manager found, let's autodetect
    echo "manager: $manager"
    echo "detecting manager"
    _detect_manager
fi

# user queried project name, but no virtualenvwrapper, using  pyenv-virtualenv
# if command -v pyenv > /dev/null 2>&1 && pyenv commands | grep -q "virtualenvwrapper"; then
if [ -n "$manager" ] && [ "$manager" = "pyenv_virtualenv" ]; then
#if [ -n $manager && $manager -eq 'pyenv_virtualenv' ] || [ pyenv commands | grep -q "virtualenv$" ]; then
    if $(pyenv virtualenvs $project_name | grep -q $project_name); then
        echo "pyenv activate $project_name"
       #pyenv activate $project_name
    else
        echo "pyenv virtualenv $project_name"
       #pyenv virtualenv $project_name
    fi
fi
