#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dockerdb


def test_helloworld():
    pass


def test_docker():
    mongo = dockerdb.Mongo(tag='3.5', wait=True)
    client = mongo.pymongo_client()
    server_info = client.server_info()
    assert server_info['version'].startswith('3.5')

    mongo = dockerdb.Mongo(tag='3.4', wait=True)
    client = mongo.pymongo_client()
    server_info = client.server_info()
    assert server_info['version'].startswith('3.4')
