import dockerdb.service


def get_all_container_ids():
    all_containers = dockerdb.service.client.containers.list()
    return [c.id for c in all_containers]
