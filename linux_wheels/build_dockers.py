#!/usr/bin/env python3
import os
import shutil
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from subprocess import check_call
from pkg_resources import resource_stream

from linux_wheels.build_wheel import TARGET_PYTHONS

DOCKERS = {
    # Debian 8 (stable)
    'jessie': {},
    # Debian 9 (testing)
    'stretch': {},
    # Debian 7 (oldstable)
    'wheezy': {
        'apt_blacklist': {
            'libpython-all-dev',
            'libpython3-all-dev',
            'python-wheel',
            'python3-matplotlib',
            'python3-wheel',
        },
    },
    # Ubuntu 14.04
    'trusty': {},
    # Ubuntu 12.04
    'precise': {
        'apt_blacklist': {
            'libpython-all-dev',
            'libpython3-all-dev',
            'python-wheel',
            'python3-matplotlib',
            'python3-pip',
            'python3-tz',
            'python3-wheel',
        },
    },
}


BASE_DEBIAN_PACKAGES = frozenset({
    'build-essential',
    'ca-certificates',
    'curl',
    'cython',
    'gfortran',
    'libblas-dev',
    'liblapack-dev',
    'libpython-all-dev',
    'libpython3-all-dev',
    'python-all',
    'python-all-dev',
    'python-docutils',
    'python-matplotlib',
    'python-pip',
    'python-setuptools',
    'python-sphinx',
    'python-tz',
    'python-wheel',
    'python3-all',
    'python3-all-dev',
    'python3-docutils',
    'python3-matplotlib',
    'python3-pip',
    'python3-setuptools',
    'python3-sphinx',
    'python3-tz',
    'python3-wheel',
    'wget',
})

APT_SOURCES_FIX = '''\
RUN sed -i 's/httpredir\.debian\.org/mirrors.ocf.berkeley.edu/g' /etc/apt/sources.list
RUN sed -i 's/security\.debian\.org/mirrors.ocf.berkeley.edu\/debian-security/g' /etc/apt/sources.list
RUN sed -i 's/archive\.ubuntu\.com/mirrors.ocf.berkeley.edu/g' /etc/apt/sources.list
'''

DUMB_INIT_INSTALL = '''\
RUN wget -O /tmp/dumb-init.deb \
        https://github.com/Yelp/dumb-init/releases/download/v1.0.0/dumb-init_1.0.0_amd64.deb \
    && dpkg -i /tmp/dumb-init.deb \
    && rm /tmp/dumb-init.deb
'''

# Try to bludgeon our way into a working pip+wheel install.
# Currently we only use this on platforms without wheel easily available.
PIP_INSTALL = r'''\
RUN wget -O /tmp/get-pip.py https://bootstrap.pypa.io/get-pip.py; \
    for p in {pythons}; do \
        if command -v "$p"; then \
            "$p" /tmp/get-pip.py; \
            "$p" -m pip.__main__ install -U wheel setuptools; \
        fi; \
    done
'''.format(pythons=' '.join(TARGET_PYTHONS))

# TODO: reduce duplication in this and the above PIP_INSTALL
PYTHON_DEPS_INSTALL = r'''\
RUN for p in {pythons}; do \
        if command -v "$p"; then \
            "$p" -m pip.__main__ install pip-custom-platform; \
        fi; \
    done
'''.format(pythons=' '.join(TARGET_PYTHONS))

ADD_BUILD_WHEEL = '''\
COPY build-wheel /usr/local/bin/build-wheel
RUN chmod +x /usr/local/bin/build-wheel
'''


def build_apt_install(packages):
    return (
        'RUN apt-get update '
        '&& DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends {} '
        '&& apt-get clean\n'
    ).format(
        ' '.join(packages)
    )


@contextmanager
def chdir(path):
    orig = os.getcwd()
    os.chdir(str(path))
    yield
    os.chdir(orig)


def build_docker(dist):
    # TODO: Once the images are built, we should drop to a non-root user
    # (slightly more protection against kernel vulnerabilities).
    print('Building docker: {}'.format(dist))
    params = DOCKERS[dist]
    tag = 'docker.ocf.berkeley.edu:5000/builder-{}'.format(dist)

    with resource_stream(__package__, os.path.join('Dockerfiles', dist)) as f:
        template = f.read().decode('utf8')

    apt_packages = (
        (BASE_DEBIAN_PACKAGES | params.get('extra_apt_install', set())) -
        params.get('apt_blacklist', set())
    )
    replacements = {
        ('{DUMB_INIT_INSTALL}', DUMB_INIT_INSTALL),
        ('{APT_SOURCES_FIX}', APT_SOURCES_FIX),
        ('{APT_INSTALL}', build_apt_install(apt_packages)),
        ('{PIP_INSTALL}', PIP_INSTALL),
        ('{PYTHON_DEPS_INSTALL}', PYTHON_DEPS_INSTALL),
        ('{ADD_BUILD_WHEEL}', ADD_BUILD_WHEEL),
        ('{ENTRYPOINT}', 'ENTRYPOINT ["/usr/bin/dumb-init", "/usr/local/bin/build-wheel"]'),
    }
    for key, replacement in replacements:
        template = template.replace(key, replacement)

    tempdir = Path(tempfile.mkdtemp())
    try:
        with (tempdir / 'Dockerfile').open('w') as f:
            f.write(template)
        shutil.copyfile(os.path.join(os.path.dirname(__file__), 'build_wheel.py'), str(tempdir / 'build-wheel'))

        with chdir(tempdir):
            check_call(('docker', 'build', '--no-cache', '-t', tag, '.'))
        check_call(('docker', 'push', tag))
    finally:
        shutil.rmtree(str(tempdir))


def main(argv=None):
    # TODO: better argparsing
    if len(sys.argv) == 2:
        # this is disgusting
        if sys.argv[1] == '--list':
            print('\n'.join(sorted(DOCKERS.keys())))
        else:
            build_docker(sys.argv[1])
    else:
        for docker in DOCKERS:
            build_docker(docker)


if __name__ == '__main__':
    exit(main())
