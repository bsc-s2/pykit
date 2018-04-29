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
    except docker.errors.NotFound as e:
        dd(repr(e))

    ipam_pool = docker.utils.create_ipam_pool(**net_config[net_name])

    ipam_config = docker.utils.create_ipam_config(
        pool_configs=[ipam_pool]
    )

    dcli.create_network(net_name, driver="bridge", ipam=ipam_config)


def start_container(name, image,
                    ip=None,
                    command='',
                    port_bindings=None,
                    env=None):

    net_name = 'network1'
    dcli = get_client()

    kwargs = {}
    if env is not None:
        kwargs['environment'] = env

    if port_bindings is not None:
        kwargs['ports'] = port_bindings.keys()
        kwargs['host_config'] = dcli.create_host_config(
            port_bindings=port_bindings
        )

    if ip is not None:
        net_cfg = dcli.create_networking_config({
            net_name: dcli.create_endpoint_config(ipv4_address=ip,)
        })
        kwargs['networking_config'] = net_cfg

    if not does_container_exist(name):
        dcli.create_container(
            name=name,
            image=image,
            command=command,
            **kwargs
        )

    dcli.start(container=name)


def pull_image(image):

    dcli = get_client()

    # 'daocloud.io/zookeeper:3.4.10' --> ('daocloud.io/zookeeper', '3.4.10')
    rst = dcli.pull(*image.split(':'))
    dd(rst)
