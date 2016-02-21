#!/usr/bin/env python3
"""Build (or find) wheels for a package.

The shebang says Python 3, but we really want it to work on Python 2.7 and
Python 3.2+.

We can build wheels for multiple versions without this script running that
interpreter, though.
"""
import distutils.spawn
import os
import sys
import tempfile
from subprocess import check_call

TARGET_PYTHONS = ('python2.7', 'python3.3', 'python3.4', 'python3.5')


def build_wheel(spec, python='python3.4'):
    """Return a wheel, returning the pathname to it."""
    tmp = tempfile.mkdtemp()
    os.chdir(tmp)
    check_call((python, '-m', 'pip', 'install', '--download', tmp, '--', spec))

    path, = os.listdir(tmp)
    path = os.path.join(tmp, path)
    basename, ext = path.split('.', 1)  # splitext handles ".tar.gz" weird

    # splitext can't handle .tar.gz and it's not straightforward to do
    # ourselves (e.g. we might get "numpy-1.10.4.tar.gz")
    if path.endswith('.whl'):
        return path
    elif path.endswith('.tar.gz'):
        wheel_dir = os.path.join(tmp, 'wheelhouse')
        os.mkdir(wheel_dir)
        check_call((python, '-m', 'pip.__main__', 'wheel', '-w', wheel_dir, '--', path))

        whl, = os.listdir(wheel_dir)
        assert whl.endswith('.whl')
        return os.path.join(wheel_dir, whl)
    else:
        raise AssertionError('Don\'t know how to handle downloaded file: {}'.format(path))


def build_wheels(spec, pythons=TARGET_PYTHONS):
    for python in TARGET_PYTHONS:
        if distutils.spawn.find_executable(python):
            wheel = build_wheel(spec, python=python)
            if wheel:
                print('Wheel built at {} ({})'.format(wheel, python))
                yield wheel
            else:
                print('No wheel could be found/built for {}'.format(python))
        else:
            print('Interpreter {} not found, skipping...'.format(python))


def upload_wheels(wheels):
    pass


if __name__ == '__main__':
    spec = sys.argv[1]
    wheels = list(build_wheels(spec))
    if wheels:
        print('Found these wheels: {}'.format(wheels))
        upload_wheels(wheels)
    else:
        print('No wheels were built, exiting.')
