from django.urls import reverse

menu = {
    'module_system': {
        'child': [
            {
                'name': 'system_network',
                'title': '网络配置',
                'href': reverse('module_system:system_network:device_list'),
            },
        ]
    }
}
