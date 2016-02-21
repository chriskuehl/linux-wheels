#!/usr/bin/env python3
# TODO: this is a leftover from when this was just a collection of scripts and
# not a package, combine this into a chronos module.
import json
import uuid

import requests


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
    }


def submit_job(job):
    resp = requests.post(
        CHRONOS,
        data=json.dumps(job),
        headers={'Content-Type': 'application/json'},
    )
    print(resp)
    print(resp.headers)
    print(resp.text)


def main(argv=None):
    image = 'docker.ocf.berkeley.edu:5000/builder-jessie'
    command = 'numpy'

    # TODO: we can probably use meaningful job names?
    job_name = str(uuid.uuid4())
    print(job_name)
    job = construct_job(job_name, image, command)
    submit_job(job)


if __name__ == '__main__':
    exit(main())
