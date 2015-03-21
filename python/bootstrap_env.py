#!/usr/bin/env python

from __future__ import absolute_import, division, print_function, \
    with_statement, unicode_literals


import os
import sys
import subprocess
import platform
import argparse


def warning(*objs):
    print("WARNING: ", *objs, file=sys.stderr)


def fail(message):
    sys.exit("Error: {message}".format(message=message))


PY2 = sys.version_info[0] == 2
if PY2:
    from urllib import urlretrieve
else:
    from urllib.request import urlretrieve


def has_module(module_name):
    try:
        import imp
        imp.find_module(module_name)
        del imp
        return True
    except ImportError:
        return False


def which(exe=None, throw=True, print_message=False):
    """Return path of bin. Python clone of /usr/bin/which.

    from salt.util - https://www.github.com/saltstack/salt - license apache

    :param exe: Application to search PATHs for.
    :type exe: string
    :param throw: Raise ``Exception`` if not found in paths
    :type throw: bool
    :rtype: string

    """
    if exe:
        if os.access(exe, os.X_OK):
            return exe

        # default path based on busybox's default
        default_path = '/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin'
        search_path = os.environ.get('PATH', default_path)

        for path in search_path.split(os.pathsep):
            full_path = os.path.join(path, exe)
            if os.access(full_path, os.X_OK):
                return full_path

        message = (
            '{0!r} could not be found in the following search '
            'path: {1!r}'.format(
                exe, search_path
            )
        )

        if throw:
            raise Exception(message)
        elif print_message:
            print(message)
    return None


project_dir = os.path.dirname(os.path.realpath(__file__))
env_dir = os.path.join(project_dir, '.env')
env_bin_dir = os.path.join(env_dir, 'bin')
activate_this = os.path.join(env_bin_dir, 'activate_this.py')
pip_bin = os.path.join(env_dir, 'bin', 'pip')
fabric_bin = os.path.join(env_dir, 'bin', 'fab')
fabric_exists = os.path.exists(fabric_bin) and env_bin_dir in fabric_bin
python_bin = os.path.join(env_dir, 'bin', 'python')
virtualenv_bin = which('virtualenv', throw=False)
virtualenv_exists = os.path.exists(env_dir) and os.path.isfile(python_bin)
vagrant_bin = which('vagrant', throw=False)
vagrant_exists = vagrant_bin and os.path.exists(vagrant_bin)
project_requirements_filepath = os.path.join(project_dir, 'requirements.txt')
in_virtualenv = env_bin_dir in os.environ['PATH']

try:
    import virtualenv
except ImportError:
    if not in_virtualenv:
        message = (
            'Virtualenv is required for this bootstrap to run.\n'
            'Install virtualenv via:\n'
            '\t$ [sudo] pip install virtualenv'
        )
        fail(message)


try:
    import pip
except ImportError:
    message = (
        'pip is required for this bootstrap to run.\n'
        'Find instructions on how to install at: %s' %
        'http://pip.readthedocs.org/en/latest/installing.html'
    )
    fail(message)


def check_for_curl():
    curl_bin = which('curl', throw=False)

    if not curl_bin:
        fail(
            'curl is required to install pynev. Please install this to proceed.'
        )
    else:
        return True


"""

Check for python
Check for curl
Accept cwd to run from
Accept virtualenv / project_name
Accept command to run to install project (
    'pip install -r requirements.txt'
    'pip install -e dir'
)
"""
parser = argparse.ArgumentParser()
parser.add_argument('-d', '--cwd', metavar='cwd', help='Current working directory. Defaults to shell $PWD.')
parser.add_argument('-c', '--command',
                    metavar='command',
                    help='command to run after to bootstrapped env, useful for installing packages. uses cwd.',
                    required=False, default=None
                    )
parser.add_argument('project', metavar='project', help='name of your project')


def main():
    args = parser.parse_args()
    print(args)


class VirtualEnv(object):
    """The three virtualenv types have different creation commands."""

    def create_env(self):
        pass

    @property
    def paths(self):
        pass

    @property
    def exists(self):
        """Does virtualenv exist?"""
        pass

def create_pyenv_virtualenv():
    pass

def create_virtualenv():
    pass

def create_virtualenvwrapper():
    pass


def oldmain():
    if not virtualenv_exists:
        virtualenv_bin = which('virtualenv', throw=False)

        subprocess.check_call(
            [virtualenv_bin, env_dir]
        )

    if not fabric_exists:
        execfile(activate_this, dict(__file__=activate_this))
        subprocess.check_call(
            [pip_bin, 'install', '-r', project_requirements_filepath]
        )

    if not vagrant_exists:
        message = (
            'Vagrant is required to use this on a developer box.'
            'http://docs.vagrantup.com/v2/getting-started/index.html'
        )
        print(message)

    if not in_virtualenv:
        fail("Enter your virtualenv: 'source .env/bin/activate'")

if __name__ == '__main__':
    main()
