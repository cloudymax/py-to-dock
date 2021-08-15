# program to iteratively build docker muti-stage docker images using anisble
from os import environ, remove
from dictor import dictor
import io_tools as io
import docker
from docker.api import image, network

def new_client():
    return docker.from_env()

def set_mounts(settings):              # creates and returns docker Mount() type objects

    # tons more options here: https://docker-py.readthedocs.io/en/stable/api.html#docker.types.Mount
    # https://programtalk.com/python-examples/docker.types.Mount/
    # you have to return a list of the string representation of function calls, holy shit thats jank.
    #   mounts=[
    #       docker.types.Mount(target='/test', source=vol_name),
    #       docker.types.Mount(target='/test', source=vol_name),
    #   ]

    volume_info = dictor(settings, 'volume_info')
    volumes = dictor(settings, 'volumes')

    mounts = []
    for volume in volume_info:
        source=volume_info[volume]
        target=volumes[volume]
        type="bind"
        read_only="False",
        consistency=None,
        propagation=None,
        no_copy=False,
        labels=None,
        driver_config=None,
        tmpfs_size=None,
        tmpfs_mode=None

        mount_string = f'docker.types.Mount({target}, {source}, type={type})'
        #, read_only="{read_only}", consistency="{consistency}", propagation="{propagation}", no_copy="{no_copy}", labels="{labels}", driver_config="{driver_config}", tmpfs_size="{tmpfs_size}", tmpfs_mode="{tmpfs_mode}")'''

        mounts.append(mount_string)

    return mounts

def pull_image(client, settings):      # pulls the docker image:version
    #regex a image + version into format
    image  = dictor(settings, 'container.image')
    version = dictor(settings, 'container.version')
    string = image + ":" + version

    # pull the image
    client.images.pull(string)

def set_env(settings, debug):          # creates and returns formatted environment variables
    environment_variables = {}
    env = dictor(settings, 'environment')
    for item in env:
        environment_variables[item] = dictor(settings, f"environment.{item}")

    io.print_pretty(environment_variables, debug)
    return environment_variables

def create_container(client, settings, debug):
    settings['mount_points'] = set_mounts(settings)

    if 'container' in settings:
        _name = settings['container']['name']
        _image = settings['container']['image']
        _version = settings['container']['version']
        _auto_remove = settings['container']['auto_remove']

        if 'entrypoint' in settings['container']:
            _entrypoint = settings['container']['entrypoint']
        else:
            _entrypoint = "/bin/sh"

    if 'network' in settings:
        _network_mode = settings['network']['network_type']
    else:
        _network_mode = "bridged"

    if 'mount_points' in settings:
        _mounts = settings['mount_points']
    else:
        _mounts = "[]"

    if 'environment' in settings:
        _environment = set_env(settings, debug)
    else:
        _environment = ""

    container = client.containers.create(
        name = _name,
        image = _image,
        version = _version,
        auto_remove = _auto_remove,
        network_mode = _network_mode,
        #mounts = _mounts,
        environment = _environment,
        entrypoint = _entrypoint,
    )

    return container

def run_container(container, settings, run_detached, debug=False):

    #print(f"{_name},{_image},{_version},{_auto_remove},{_network_mode},{_mounts},{_environment}")

    # run the docker image
    container.exec_run(
        cmd = settings['container']['entrypoint'],
        stdout = True,
        stdin = True,
        tty = True,
        user = "root",
        detach = run_detached,
        stream = True,
        environment = settings['environment']

    )

    #for container in client.containers.list():
    #    for line in container.logs(stream=True):
    #        io.print_pretty(line.strip(), True)

# settings data structure:
#{
#  "container": {
#    "name": "mongo_container",
#    "image": "mongo",
#    "version": "latest",
#    "mem_limit_gb": 1.5,
#    "auto_remove": false
#  },
#  "network": {
#    "host": "172.17.0.2",
#    "port": 27017,
#    "server_timeout": 3000,
#    "network_type": "bridge"
#  },
#  "volumes": {
#    "pv": "/pv",
#    "db_volume": "/db",
#    "auth_volume": "/auth",
#    "home": "/home/mongodb"
#  },
#  "init": {
#    "database_name": "test-database",
#    "collection_name": "test-collection",
#    "connection_string": "mongodb://"
#  },
#  "environment": {
#    "MONGO_INITDB_ROOT_USERNAME": "mongodb",
#    "MONGO_INITDB_ROOT_PASSWORD_FILE": "auth.json",
#    "MONGO_INITDB_DATABASE": "demo"
#  }
#}
