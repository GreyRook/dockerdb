import time

import docker


client = docker.from_env()


class Service(object):
    """Base class for docker based services"""
    timeout = 30.0

    def __init__(self, image, **kwargs):
        self.client = client
        kwargs.setdefault('detach', True)
        self.container = client.containers.run(image, **kwargs)

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


class Mongo(Service):
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
        port = 27017
        return pymongo.MongoClient(server, port, socketTimeoutMS=1000, connectTimeoutMS=1000)
