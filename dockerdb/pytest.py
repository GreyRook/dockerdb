from __future__ import absolute_import
import os
import shutil

import pytest
import dockerdb


CONTAINER_CACHE = {}


def insert_data(client, data):
    for db in data:
        for collection in data[db]:
            entries = data[db][collection]
            re = client[db][collection].insert_many(entries)


def mongorestore(service, restore):
    dst = os.path.join(service.share, 'dump')
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(restore, dst)
    service.container.exec_run(['mongorestore', dst])


def get_service(version):
    service = CONTAINER_CACHE[version]
    service.wait()
    service.factory_reset()
    return service


def ensure_service(version, port):
    if version not in CONTAINER_CACHE:
        CONTAINER_CACHE[version] = dockerdb.Mongo(
            version, wait=False, port=port)


def mongo_fixture(scope='function', versions=['latest'], data=None,
                  restore=None, reuse=True, port=27017):
    """create ficture for py.test

    Attributes:
        scope (str): py.test scope for this fixture
        versions (list): mongodb versions that should be tested
        data (dict): A dict containing data to be inserted into the database
            before the test.  The structure must be:
            {'db': {
                'collection': [
                    {'document_data': True},
                    {'another': 'document'},
                    ...
                ]
            }}

        restore (str): path to directory containing a mongo dump
        reuse (bool): wether to reuse containers or create a new container
            for every requested injection
    """

    # parallelized start of different versions
    if reuse:
        for version in versions:
            ensure_service(version, port)

    @pytest.fixture(scope=scope,  params=versions)
    def mongo(request):
        if reuse:
            service = get_service(request.param)
        else:
            service = dockerdb.Mongo(request.param, wait=True, port=port)
        client = service.pymongo_client()

        if data:
            insert_data(client, data)

        if restore:
            mongorestore(service, restore)

        yield service

        if not reuse:
            service.remove()

    return mongo
