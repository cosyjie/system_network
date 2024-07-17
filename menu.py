from django.urls import reverse_lazy

menu = {
    'module_system': {
        'child': [
            {
                'name': 'system_network',
                'title': '网络配置',
                'href': reverse_lazy('module_system:system_network:device_list'),
            },
        ]
    }
}
