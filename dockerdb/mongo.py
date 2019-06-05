import dockerdb.service


class Mongo(dockerdb.service.Service):
    """Mongo in a docker container

    Starts docker on a it's default port:
    ```
    db_docker = dockerdb.Mongo('4.0.0', wait=True)
    ```

    """
    name = 'mongo'
    mongo_port = 27017

    def __init__(self, tag, wait=False, exposed_port=None, replicaset=None, **kwargs):
        """

        * port - expose database to host on `port`
        * wait - if true the call blocks until MongoDB is ready to accept clients
        """
        self.exposed_port = exposed_port

        if replicaset is True:
            replicaset = 'rs0'

        self.replicaset_ready = False
        self.replicaset = replicaset

        kwargs['command'] = ['mongod', '--bind_ip', '0.0.0.0']
        if replicaset:
            kwargs['command'].extend(['--replSet', replicaset])

        ports = {}
        if exposed_port:
            container_port = '{}/tcp'.format(self.mongo_port)
            ports[container_port] = ('127.0.0.1', exposed_port)
        super(Mongo, self).__init__('mongo:' + tag, ports=ports, **kwargs)

    def check_ready(self):
        """Check if something responds to ``url``."""
        import pymongo.errors

        client = self.pymongo_client()
        try:
            is_master = client.admin.command('ismaster')
        except pymongo.errors.ConnectionFailure:
            return False

        if self.replicaset and not self.replicaset_ready:
            host = '{}:{}'.format(self.ip_address(), self.exposed_port)
            conf = {
                '_id': self.replicaset,
                'members': [{'_id': 0, 'host': host}]
            }
            try:
                client.admin.command('replSetInitiate', conf)
                self.replicaset_ready = True
            except pymongo.errors.OperationFailure:
                # already initlized
                self.replicaset_ready = True
            except pymongo.errors.NetworkTimeout:
                # for some reason this likes to time out
                return False

        if self.replicaset:
            return is_master.get('ismaster', False)
        return True

    def client_args(self):
        if dockerdb.inside_docker:
            ip = self.ip_address()
            port = self.mongo_port
        else:
            ip = '127.0.0.1'
            port = self.exposed_port

        host = '{}:{}'.format(ip, port)
        return {
            'host': [host],
            'socketTimeoutMS': 200,
            'connectTimeoutMS': 200
        }

    def pymongo_client(self):
        if self.exposed_port is None:
            raise AttributeError('can only connect when exposed to host')
        import pymongo
        return pymongo.MongoClient(**self.client_args())

    def asyncio_client(self):
        if self.exposed_port is None:
            raise AttributeError('can only connect when exposed to host')
        import motor.motor_asyncio
        return motor.motor_asyncio.AsyncIOMotorClient(**self.client_args())

    def factory_reset(self):
        """factory reset the database"""
        client = self.pymongo_client()
        for db in client.database_names():
            if db not in ('admin', 'config', 'local'):
                client.drop_database(db)
