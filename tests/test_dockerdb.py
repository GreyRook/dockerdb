#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dockerdb


class LazyHTTP(dockerdb.HTTPServer):
    port = 8000

    def __init__(self, wait=False, **kwargs):
        command = [
            'python3',
            '-c',
            'import http.server; import time; time.sleep(0.1); http.server.test(port=8000)'
        ]
        dockerdb.Service.__init__(self, 'python:3', command=command)


def get_all_container_ids():
    all_containers = dockerdb.client.containers.list()
    return [c.id for c in all_containers]


def test_remove():
    """container removale is tested in test_timeout and test_mongo
       on containers that are created anyway to improve test run
       performance"""
    pass


def test_http_and_wait():
    http_server = LazyHTTP(wait=False)
    assert http_server.check_ready() == False
    http_server.wait()
    assert http_server.check_ready() == True


def test_timeout():
    http_server = LazyHTTP(wait=False)
    assert http_server.check_ready() == False
    http_server.wait(timeout=0)
    assert http_server.check_ready() == False

    # test rm container
    assert http_server.container.id in get_all_container_ids()
    http_server.remove()
    assert http_server.container.id not in get_all_container_ids()


def test_mongo():
    """test different versions of mongo"""
    mongo = dockerdb.Mongo(tag='3.5', wait=True)

    start_time = str(dockerdb.start_time)
    assert start_time in mongo.container.name
    assert 'mongo' in mongo.container.name

    client = mongo.pymongo_client()
    server_info = client.server_info()
    assert server_info['version'].startswith('3.5')

    # test docker container removable by gc
    mongo_id = mongo.container.id
    assert mongo_id in get_all_container_ids()
    del mongo
    assert mongo_id not in get_all_container_ids()


    # test mongo 3.4
    mongo = dockerdb.Mongo(tag='3.4', wait=True)
    client = mongo.pymongo_client()
    server_info = client.server_info()
    assert server_info['version'].startswith('3.4')

    mongo_id = mongo.container.id
    del mongo
    assert mongo_id not in get_all_container_ids()
