#!/usr/bin/env python3
"""Build (or find) wheels for a package.

The shebang says Python 3, but we really want it to work on Python 2.7 and
Python 3.3+.

We can build wheels for multiple versions without this script running that
interpreter, though.

This script gets copied into Docker images, so it can't import anything else
from this package. And its dependencies should be minimal.
"""
import distutils.spawn
import os
import sys
import tempfile
from os.path import basename
from os.path import join
from subprocess import check_call

import requests

TARGET_PYTHONS = ('python2.7', 'python3.3', 'python3.4', 'python3.5')


def build_wheel(spec, python='python3.4'):
    """Return a wheel, returning the pathname to it."""
    os.environ['PIP_NO_DEPS'] = '1'  # TODO: smell

    tmp = tempfile.mkdtemp()
    os.chdir(tmp)
    check_call((python, '-m', 'pip', 'install', '--download', tmp, '--', spec))

    # TODO: what is lextab.py???
    path, = [p for p in os.listdir(tmp) if p != 'lextab.py']
    path = join(tmp, path)
    basename, ext = path.split('.', 1)  # splitext handles ".tar.gz" weird

    # splitext can't handle .tar.gz and it's not straightforward to do
    # ourselves (e.g. we might get "numpy-1.10.4.tar.gz")
    if path.endswith('.whl'):
        return path
    elif path.endswith('.tar.gz'):
        wheel_dir = join(tmp, 'wheelhouse')
        os.mkdir(wheel_dir)
        check_call((python, '-m', 'pip_custom_platform.main', 'wheel', '-w', wheel_dir, '--', path))

        whl, = os.listdir(wheel_dir)
        assert whl.endswith('.whl')
        return join(wheel_dir, whl)
    else:
        raise AssertionError('Don\'t know how to handle downloaded file: {}'.format(path))


def valid_python(python):
    """Return whether we should consider using this Python interpreter."""
    path = distutils.spawn.find_executable(python)

    # Is it even available?
    if not path:
        return False

    # If we're in a virtualenv, we're probably in a dev environment, and we
    # don't want to execute system binaries which probably won't have
    # pip-custom-platform (or other deps) available.
    venv = os.environ.get('VIRTUAL_ENV')
    if venv and not path.startswith(venv):
        return False

    return True


def build_wheels(spec, pythons=TARGET_PYTHONS):
    for python in TARGET_PYTHONS:
        if valid_python(python):
            wheel = build_wheel(spec, python=python)
            if wheel:
                print('Wheel built at {} ({})'.format(wheel, python))
                yield wheel
            else:
                print('No wheel could be found/built for {}'.format(python))
        else:
            print('Interpreter {} not valid, skipping...'.format(python))


def upload_wheel(path):
    os.environ.setdefault('WHEEL_UPLOAD_URL', 'http://localhost:6789/upload')
    resp = requests.post(
        os.environ['WHEEL_UPLOAD_URL'],
        files=[
            ('file', (basename(path), open(path, 'rb'), 'application/octet-stream')),
        ],
    )
    assert resp.status_code == 204, resp.status_code


def main(argv=None):
    spec = sys.argv[1]
    wheels = list(build_wheels(spec))
    if wheels:
        print('Found these wheels: {}'.format(wheels))
        for wheel in wheels:
            upload_wheel(wheel)
    else:
        print('No wheels were built, exiting.')

    # TODO: we need to remove our Chronos job manually here


if __name__ == '__main__':
    exit(main())
