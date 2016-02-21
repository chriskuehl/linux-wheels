from setuptools import find_packages
from setuptools import setup

setup(
    name='linux_wheels',
    version='0.0.1',
    author='Chris Kuehl',
    author_email='ckuehl@ocf.berkeley.edu',
    packages=find_packages(),
    package_data={
        'linux_wheels': ['dockerfiles/*'],
    },
    install_requires=(),
    entry_points={
        'console_scripts': [
            'lw-build-dockers = linux_wheels.build-dockers:main',
            'lw-build-wheel = linux_wheels.build_wheel:main',
            'lw-launch-job = linux_wheels.launch_job:main',
            'lw-remove-chronos-jobs = linux_wheels.build_wheel:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)
