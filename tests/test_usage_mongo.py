import os

import pytest
import dockerdb.pytest

BASE_PATH = os.path.dirname(__file__)
DUMP_PATH = os.path.join(BASE_PATH, 'dump')
DATA = {
    'dbname': {
        'user_collection':
            [
                {'user': 'admin', 'password': 'secret'}
            ]
    }
}

# have two different versions of mongo with static data
mongo = dockerdb.pytest.mongo_fixture(versions=["3.4", "3.5"], data=DATA)

# with data from a mongodump backup
mongo2 = dockerdb.pytest.mongo_fixture(versions=["3.4"], restore=DUMP_PATH)


def test_package_consistent():
    # ensure restore path does actually exist
    assert os.path.exists(os.path.join(DUMP_PATH, 'test', 'user.bson'))
    assert os.path.exists(os.path.join(DUMP_PATH, 'test', 'user.metadata.json'))


def test_mongo_1(mongo):
    # this should be run twice
    client = mongo.pymongo_client()
    users = client['dbname']['user_collection']
    user = users.find_one({'user': 'admin'})
    assert user['password'] == 'secret'

    # changes to db should not persist to next test
    users.update({'user': 'admin'}, {'password': 'public'})


def test_mongo_2(mongo):
    # mongo db should be cleared after test_mongo_1
    client = mongo.pymongo_client()
    users = client['dbname']['user_collection']
    user = users.find_one({'user': 'admin'})
    assert user['password'] == 'secret'
    assert users.find().count() == 1


def test_mongo_restore(mongo2):
    client = mongo2.pymongo_client()
    users = client['test']['user']
    user = users.find_one({'user': 'admin'})
    assert user['password'] == 'reallysecret'
