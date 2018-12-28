#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

import docker
import dockerdb.service

from .common import get_all_container_ids


class LazyHTTP(dockerdb.HTTPServer):
    port = 8000

    def __init__(self, **kwargs):
        dockerdb.service.client.images.pull('python:3.7')
        command = [
            'python3',
            '-c',
            'import http.server; import time; time.sleep(0.1); http.server.test(port=8000)'
        ]
        dockerdb.Service.__init__(self, 'python:3.7', command=command, **kwargs)


@pytest.mark.timeout(10)
def test_http_and_wait():
    http_server = LazyHTTP(wait=False)
    assert http_server.check_ready() == False
    http_server.wait()
    assert http_server.check_ready() == True


@pytest.mark.timeout(10)
def test_timeout():
    http_server = LazyHTTP(wait=False)
    assert http_server.check_ready() == False
    http_server.wait(timeout=0)
    assert http_server.check_ready() == False

    # test rm container
    assert http_server.container.id in get_all_container_ids()
    http_server.remove()
    assert http_server.container.id not in get_all_container_ids()

