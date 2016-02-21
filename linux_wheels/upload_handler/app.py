#!/usr/bin/env python3
import os
import re

from flask import Flask
from flask import request

UPLOAD_PATH = '/srv/linux-wheels/wheelhouse/'


app = Flask(__name__)


@app.route('/upload', methods={'POST'})
def upload():
    # TODO: This needs to do some kind of verification to prevent malicious
    # packages from uploading whatever files they want (and replacing
    # legitimate wheels from legitimate packages with malicious ones).
    f = request.files['file']
    assert f
    assert re.match(r'^[a-zA-Z0-9\-_\.]+\.whl$', f.filename)

    path = os.path.realpath(os.path.join(UPLOAD_PATH, f.filename))
    assert path.startswith(UPLOAD_PATH)

    f.save(path)
    return ('', 204)


def main(argv=None):
    app.run(host='0.0.0.0', port=6789, debug=True)


if __name__ == '__main__':
    exit(main())
