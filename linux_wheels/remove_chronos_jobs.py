#!/usr/bin/env python3
import json
import requests
import uuid
from datetime import datetime


CHRONOS = 'http://hozer-70:4400'

def list_jobs():
    resp = requests.get(CHRONOS + '/scheduler/jobs')
    return resp.json()

def submit_job(job):
    resp = requests.post(
        CHRONOS,
        data=json.dumps(job),
        headers={'Content-Type': 'application/json'},
    )


def remove_job(job):
    resp = requests.delete(
        CHRONOS + '/scheduler/job/' + job['name'],
    )


def main(argv=None):
    jobs = list_jobs()
    print('Deleting {} jobs...'.format(len(jobs)))
    for i, job in enumerate(jobs):
        if i % 100 == 0:
            print('Progress: {}/{}'.format(i, len(jobs)))
        remove_job(job)


if __name__ == '__main__':
    exit(main())