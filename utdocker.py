import docker

from pykit import ututil

dd = ututil.dd

# default network config for unittest
net_config = {
    'network1': {
        'subnet': '192.168.52.0/24',
        'gateway': '192.168.52.254',
    }
}


def get_client():
    dcli = docker.Client(base_url='unix://var/run/docker.sock')
    return dcli


def does_container_exist(name):

    dcli = get_client()

    try:
        dcli.inspect_container(name)
        return True
    except docker.errors.NotFound:
        return False


def stop_container(*names):

    dcli = get_client()
    for name in names:
        try:
            dcli.stop(container=name)
        except Exception as e:
            dd(repr(e), ' while trying to stop docker container: ' + repr(name))


def remove_container(*names):

    dcli = get_client()

    for name in names:
        try:
            dcli.kill(name)
        except Exception as e:
            dd(repr(e) + ' while killing container: ' + repr(name))

        try:
            dcli.remove_container(name)
        except Exception as e:
            dd(repr(e) + ' while removing container: ' + repr(name))


def create_network():

    net_name = 'network1'
    dcli = get_client()

    try:
        dcli.inspect_network(net_name)
        return
    except docker.errors.NotFound:
        pass

    ipam_pool = docker.utils.create_ipam_pool(**net_config[net_name])

    ipam_config = docker.utils.create_ipam_config(
        pool_configs=[ipam_pool]
    )

    dcli.create_network(net_name, driver="bridge", ipam=ipam_config)


def start_container(name, image, ip, command):

    net_name = 'network1'
    dcli = get_client()

    net_cfg = dcli.create_networking_config({
        net_name: dcli.create_endpoint_config(ipv4_address=ip,)
    })

    if not does_container_exist(name):
        dcli.create_container(
            name=name,
            image=image,
            networking_config=net_cfg,
            command=command,
        )

    dcli.start(container=name)
