#!/usr/bin/env python3
import requests


CHRONOS = 'http://hozer-70:4400'


def list_jobs():
    resp = requests.get(CHRONOS + '/scheduler/jobs')
    return resp.json()


def remove_job(job):
    requests.delete(
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
