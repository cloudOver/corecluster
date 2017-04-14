MODULE = {
    'models': ['corecluster.models.core'],
    'api': [
        'corecluster.views.admin',
        'corecluster.views.api',
        'corecluster.views.user',
    ],
    'ci': [
        'corecluster.views.ci',
    ],
    'configs': {
        'core': '/etc/corecluster/config.py',
        'hardware': '/etc/corecluster/hardware.py',
        'agent': '/etc/corecluster/agent.py',
    },
    'hooks': {
        'agent.vm.create': ['corecluster.hooks.vm'],
        'agent.vm.remove_vm': ['corecluster.hooks.vm'],
        'cron.minute': ['corecluster.hooks.node_libvirt'],
        'cron.hourly': ['corecluster.hooks.vm_cleanup_db', 'corecluster.hooks.vm_cleanup_task'],
    },
    'agents': [
        {'type': 'vm', 'module': 'corecluster.agents.vm', 'count': 4},
        {'type': 'network', 'module': 'corecluster.agents.network', 'count': 4},
        {'type': 'console', 'module': 'corecluster.agents.console', 'count': 1}
    ],
    'drivers': {

    },
    'algorithms': {

    },
}
