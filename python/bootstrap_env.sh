#!/bin/sh
# ENV variables accepted:
# PYBOOTSTRAP_DIR: directory of your configs

set -e

# TODO: bootstrap bootstrap, check for pip, install pystrap

# this step is needed because only shell can source into an environment.
#project_config_dir="$( python bootstrap_env.py $@ --get-project-config)"

my_needed_commands="git python"

missing_counter=0
for needed_command in $my_needed_commands; do
  if ! command -v "$needed_command" >/dev/null 2>&1; then
    echo "Command not found in PATH: $needed_command\n" >&2
    missing_counter=$(( missing_counter += 1 ))
  fi
done

if [ $missing_counter -gt 0 ]; then
  echo "Minimum $missing_counter commands are missing in PATH, aborting.\n" >&2
  exit 1
fi

if env | grep -q ^VIRTUAL_ENV=
then
    in_virtualenv="in_virtualenv"
fi


if command -v virtualenv > /dev/null 2>&1
then
    has_virtualenv="has_virtualenv"
fi

if env | grep -q ^PYENV_ROOT=
then
    has_pyenv="has_pyenv"
fi


if env | grep -q ^PYENV_VIRTUALENV_INIT=
then
    has_pyenv_virtualenv="has_pyenv_virtualenv"
fi

if env | grep -q ^VIRTUALENVWRAPPER_VIRTUALENV=
then
    has_virtualenvwrapper="has_virtualenvwrapper"
fi

# user outside of virtualenv without virtualenv installed.
if [ ! -n "$in_virtualenv" ] && [ ! -n "$has_virtualenv" ]; then
    cat <<EOF
You must install virtualenv, see:
https://virtualenv.pypa.io/en/latest/installation.html
EOF
    exit 1
fi




_detect_manager() {
    if [ -n "$has_pyenv" ]; then # has pyenv
        if [ -n "$has_pyenv_virtualenv" ]; then # has virtualenv extension for pyenv
            if [ -n "$has_pyenv_virtualenvwrapper" ]; then  # confusing you? pyenv-virtualenvwrapper
                echo "virtualenvwrapper"
            else
                echo "pyenv-virtualenv"
            fi
        else  
            echo "virtualenv"
        fi
    else
        if [ -n "$has_virtualenvwrapper" ]; then
            echo "virtualenvwrapper"
        else
            echo "virtualenv"
        fi
    fi
}


_virtualenv_project() {
    if [ -d "$HOME/.virtualenvs/$project_name" ]; then
        echo "environment found"
    else
        echo "no environment"
        virtualenv "$HOME/.virtualenvs/$project_name"
        . "$HOME/.virtualenvs/$project_name/bin/activate"
    fi
}


_virtualenvwrapper_project() {
    if $(lsvirtualenv | grep -q "^$project_name"); then
        workon $project_name
    else
        mkvirtualenv $project_name
        workon $project_name
    fi
}

_pyenv_virtualenv() {
    if $(pyenv virtualenvs $project_name | grep -q "$project_name"); then
        echo "pyenv activate $project_name"
       #pyenv activate $project_name
    else
        echo "pyenv virtualenv $project_name"
       #pyenv virtualenv $project_name
    fi
}

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

project_name=$@

if [ "$vflag" = "on" ]; then
    echo "project_name: $project_name"
    echo "install_command: $install_command"
    echo "manager: $manager"
fi

if [ -z "$project_name" ]; then
    echo "Please enter at least a project_name."
    _print_message
    exit 1
fi



if [ -z "$manager" ]; then  # no manager found, let's autodetect
    manager=$(_detect_manager)
    echo "detected manager $manager"
fi

if [ -n "$in_virtualenv" ]; then echo "in virtualenv"; fi

# user queried project name, but no virtualenvwrapper
# user queried project name, but no virtualenvwrapper, using  pyenv-virtualenv
if [ -n "$manager" ] && [ "$manager" = "pyenv-virtualenv" ]; then
    _pyenv_virtualenv    
fi


eval "$install_command"
