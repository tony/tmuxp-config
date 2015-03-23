#!/usr/bin/env python
"""
Bootstrap script to verify / prep python environments for projects.

Works with `virtualenv`_, `virtualenvwrapper`_ and `pyenv-virtualenv`_.

This script cannot place shell into a virtual environment. However, using a
bash script, it can.

Mission
-------

enhance bootstrap_env.py script to handle virtualenv, virtualenvwrapper
and  pyenv-virtualenv.

Problem:

python script alone can't source into an environment.

Solution:

pipe the whole thing through a #!/bin/sh, let the python script return the
activate script to source.

Problem:

can't keep interactive terminal while piping it into a variable

Solution:

Use a temporary file.

Problem:

Security, race conditions

Solution:

Have the shell script run a basic go-around (behind the scenes) to create and
return a project directory, to save as a variable.

The second pass through the bootstrap script, if a successful exit code is
returned, can then source the project's virtualenv activation script.


Benefits:

- Leverage the full power of argparse (without worrying about getopt's
  portability or getopts' lack of long command support.
- Abstract out common patterns' needed to bootstrap a system / python project
  under virtualenv / virtualenvwrapper / pyenv-virtualenv.
- Use one command to drop into any one of the above environments. Since
  PYBOOTSTRAP_DIR keeps a registry of projects' virtualenvs and directories.
- Shell compatibility, clear passthru of arguments and uses standard POSIX
  utilities on top of python scripting.
- Can source you right into a virtualenv for any of the 3 projects
- Can cd you into your project directory
- EDITOR shortcuts to edit a JSON config, in should your project dir or
  virtualenv change.

"""

from __future__ import absolute_import, division, print_function, \
    with_statement, unicode_literals

import os
import sys
import re
import subprocess
import platform
import argparse
import pprint

from distutils.version import LooseVersion


pp = pprint.PrettyPrinter(indent=4).pprint


def strtobool(val):
    """Convert a string representation of truth to true (1) or false (0).

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return 1
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return 0
    else:
        raise ValueError("invalid truth value %r" % (val,))


def prompt(query):
    sys.stdout.write('%s [y/n]: ' % query)
    val = raw_input()
    try:
        ret = strtobool(val)
    except ValueError:
        sys.stdout.write('Please answer with a y/n\n')
        return prompt(query)
    return ret


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


@property
def in_virtualenv():
    return 'VIRTUAL_ENV' in os.environ['PATH']

try:
    import virtualenv
except ImportError:
    if not in_virtualenv:
        message = (
            'Virtualenv is required for this bootstrap to run.\n'
            'Install virtualenv via:\n'
            '\t$ [sudo] pip install virtualenv'
        )
        # fail(message)


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
parser.add_argument(
    '-d',
    '--cwd',
    metavar='cwd',
    help='Current working directory. Defaults to shell $PWD.'
)
parser.add_argument(
    '-x', '--container', metavar='container',
    choices=['virtualenv', 'virtualenvwrapper', 'pyenv-virtualenv'],
    help='virtualenv environment you are using. Will attempt to auto-detect'
         ' based on your environment variables.'
)
parser.add_argument(
    '-c', '--command',
    metavar='command',
    help='command to run after to bootstrapped env, useful for installing packages. uses cwd.',
    required=False, default=None
)
# Internal argument to work-around shell limitations. Returns project config
# directory
parser.add_argument(
    '--get-project-config',
    dest='get_project_config',
    help=argparse.SUPPRESS,
    action='store_true'
)
parser.add_argument('project', metavar='project', help='name of your project')

BOOTSTRAP_DIR = os.path.expanduser('~/.pybootstrap')
if 'PYBOOTSTRAP_DIR' in os.environ and os.environ['PYBOOTSTRAP_DIR']:
    BOOTSTRAP_DIR = os.environ['PYBOOTSTRAP_DIR']

    if not os.path.isdir(BOOTSTRAP_DIR):
        sys.exit("BOOTSTRAP_DIR %s is not a directory." % BOOTSTRAP_DIR)

    if not os.access(BOOTSTRAP_DIR, os.W_OK):
        sys.exit("BOOTSTRAP_DIR %s is not writable." % BOOTSTRAP_DIR)

BOOTSTRAP_PROJECTS_DIR = os.path.join(BOOTSTRAP_DIR, 'projects')


class Application(object):
    """Get version of, path, installation info for applications."""
    command = None
    version_arg = None  # arg to run to get prog's version, e.g. -v

    @property
    def version(self):
        if hasattr(self, '_parse_version'):
            return self._parse_version(self._get_version())
        return self._get_version()

    @property
    def bin_path(self):
        return which(self.command)

    def _get_version(self):
        return run([self.bin_path, self.version_arg])

    def _parse_version(self, version):
        """
        :param version: version returned from self.get_version
        :type version: str
        :rtype: :class:`distutils.version.LooseVersion`
        :return: version of program
        """
        return LooseVersion(version)


class Git(Application):
    """
    Version Control System
    Homepage: http://git-scm.com/
    """
    command = 'git'
    version_arg = '--version'

    def _parse_version(self, version):
        """Parse git version 2.1.4 -> 2.1.4"""
        version = re.compile(
            r'^git version (?P<version>[0-9.]+)$',
        ).match(version).group('version')
        return super(Git, self)._parse_version(version)


def main():
    args = parser.parse_args()

    if args.get_project_config:
        project_name = args.project
        project_dir = os.path.join(BOOTSTRAP_PROJECTS_DIR, project_name)
        print(project_dir)
        sys.exit()

    g = Git()
    print(g.version)
    # prompt("Hi")

    v1 = VirtualEnv()
    v2 = PyEnvVirtualEnv()

    #: Grab the python related variables from the environment
    PYTHON_ENV = {
        k: v for k, v in os.environ.items()
        if any(_k in k for _k in ['VIRTUAL', 'PYENV', 'PYTHON'])
    }

    pp(PYTHON_ENV)

    # 1.) Detect the user's installed tools
    # virtualenv
    # virtualenvwrapper
    # pyenv
    # pyenv-virtualenv
    # pyenv-virtualenvwrapper


def gather_environment_diagnostics():
    PYTHON_ENV = {
        k: v for k, v in os.environ.items()
        if any(_k in k for _k in ['VIRTUAL', 'PYENV', 'PYTHON'])
    }






    return PYTHON_ENV


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

    def download(self):
        """Offer to download."""
        pass

    def signature(self):
        """

        :rtype: bool
        :returns: True if shell environment indicates environment found
        """

    def signature(self):
        """Return True if environmental variables indicate env is sourced.

        :rtype: bool
        :returns: True if shell environment indicates environment found
        """
        pass


def run(args, *pargs, **kwargs):
    print(args)
    return subprocess.check_output(args, *pargs, **kwargs)


class PyEnvVirtualEnv(VirtualEnv):
    """
    Homepage: https://github.com/yyuu/pyenv-virtualenv
    License: MIT
    Requirements: pyenv (https://github.com/yyuu/pyenv)
    """

    def download(self):
        # determine if pyenv exists
        pass

    def signature(self):
        """

        :rtype: bool
        :returns: True if shell environment indicates environment found
        """
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
