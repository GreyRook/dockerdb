import pytest

import dockerdb.mongo

from .common import get_all_container_ids


@pytest.mark.timeout(60)
def test_mongo():
    """test different versions of mongo"""
    mongo = dockerdb.mongo.Mongo(tag='3.5', exposed_port=27090, wait=True)

    start_time = str(dockerdb.service.start_time)
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
    mongo = dockerdb.mongo.Mongo(tag='3.4', exposed_port=27090, wait=True)
    client = mongo.pymongo_client()
    server_info = client.server_info()
    assert server_info['version'].startswith('3.4')

    mongo_id = mongo.container.id
    del mongo
    assert mongo_id not in get_all_container_ids()
