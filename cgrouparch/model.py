from cgroup_arch import blkio
from cgroup_arch import cpu

subsystem = {
    'cpu': {
        'set_cgroup': cpu.set_cgroup,
        'reset_statistics': cpu.reset_statistics,
        'get_account': cpu.get_account,
    },
    'blkio': {
        'set_cgroup': blkio.set_cgroup,
        'reset_statistics': blkio.reset_statistics,
        'get_account': blkio.get_account,
    },
}
