#!/usr/bin/env python3
# TODO: this is a leftover from when this was just a collection of scripts and
# not a package, combine this into a chronos module.
import json
import uuid
from argparse import ArgumentParser

import requests

from linux_wheels.build_dockers import DOCKERS


CHRONOS = 'http://hozer-70:4400/scheduler/iso8601'


def construct_job(job_name, image, command):
    return {
        'name': job_name,
        'container': {
            'type': 'DOCKER',
            'image': image,
            'network': 'BRIDGE',
            'forcePullImage': True,
        },
        'cpus': 0.5,
        'mem': 512,
        'command': command,
        'shell': False,
        'schedule': 'R1//PT10M',
        'environmentVariables': [{
            # what a weird way to represent a key/value dict in JSON...
            'name': 'WHEEL_UPLOAD_URL',
            'value': 'http://pypi.ocf.berkeley.edu:6789/upload',
        }],
    }


def submit_job(job):
    resp = requests.post(
        CHRONOS,
        data=json.dumps(job),
        headers={'Content-Type': 'application/json'},
    )
    assert resp.status_code == 204, resp.status_code


def main(argv=None):
    parser = ArgumentParser(description='asdf')
    # TODO: validate the specs?
    parser.add_argument('spec', type=str, nargs='+')
    args = parser.parse_args(argv)

    for spec in args.spec:
        print('Submitting jobs for {}...'.format(spec))
        for dist in DOCKERS:
            print('  - {}'.format(dist), end='')

            image = 'docker.ocf.berkeley.edu:5000/builder-{}'.format(dist)
            # TODO: if we're careful, we can probably get rid of the UUID
            job_name = '{}-{}-{}'.format(spec, dist, uuid.uuid4())
            job = construct_job(job_name, image, spec)
            submit_job(job)

            print(' done: {}'.format(job_name))


if __name__ == '__main__':
    exit(main())
