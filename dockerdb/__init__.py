__version__ = '0.4.1'
import os

import docker

docker_client = docker.from_env(version='auto')
inside_docker = os.path.exists('/.dockerenv')


def get_docker_infos():
    my_network_id = None
    with open('/proc/1/cpuset') as f:
        path = f.read()
        my_container_id = os.path.basename(path).strip()

    for network in docker_client.networks.list():
        network.reload()
        containers = [c.id for c in network.containers]
        print('network', network, containers, my_container_id in containers)
        for c in containers:
            print(my_container_id, c, c==my_container_id)
        if my_container_id in containers:
            my_network_id = network.id
            break

    print('my_container_id', my_container_id)
    return my_container_id, my_network_id


my_container_id = my_network_id = None
if inside_docker:
    my_container_id, my_network_id = get_docker_infos()

