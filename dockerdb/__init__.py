import time

import docker

start_time = int(time.time())
counter = 0
client = docker.from_env()


class Service(object):
    """Base class for docker based services"""
    timeout = 30.0
    name = 'service'

    def __init__(self, image, **kwargs):
        global counter

        self.client = client
        kwargs.setdefault('detach', True)
        name = 'tmp_{}_{}_{}'.format(start_time, self.name, counter)
        kwargs.setdefault('name', name)
        self.container = client.containers.run(image, **kwargs)
        counter += 1

    def inspect(self):
        """get docker inspect data for container"""
        return self.client.api.inspect_container(self.container.id)

    def ip_address(self):
        return self.inspect()['NetworkSettings']['IPAddress']

    def wait(self, timeout=None):
        if timeout is None:
            timeout = self.timeout

        start = time.time()
        while not self.check_ready() and time.time() - start < timeout:
            time.sleep(0.1)

    def remove(self):
        self.container.remove(force=True)

    def __del__(self):
        try:
            self.container.remove(force=True)
        except:
            pass


class HTTPServer(Service):
    protocol = 'http'
    port = '80'

    def check_ready(self):
        import requests

        ip = self.ip_address()
        url = '{}://{}:{}'.format(self.protocol, ip, self.port)

        try:
            requests.get(url)
            return True
        except requests.exceptions.ConnectionError:
            return False


class Mongo(Service):
    name = 'mongo'
    port = 27017

    def __init__(self, tag, wait=False, **kwargs):
        Service.__init__(self, 'mongo:' + tag)
        if wait:
            self.wait()

    def check_ready(self):
        """Check if something responds to ``url``."""

        client = self.pymongo_client()
        try:
            client.admin.command('ismaster')
            return True
        except pymongo.errors.ConnectionFailure:
            return False

    def pymongo_client(self):
        # lazy load pymongo
        import pymongo
        import pymongo.errors

        server = self.ip_address()
        return pymongo.MongoClient(server, self.port, socketTimeoutMS=100, connectTimeoutMS=100)
