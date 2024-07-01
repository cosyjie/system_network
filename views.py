import subprocess


from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse, reverse_lazy
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic.edit import FormView

from appcommon.helper import subprocess_run
from panel.module_system.views import ModuleSystemMixin

from .forms import Ipv4Form


class NetworkMixin(ModuleSystemMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = 'system_network'
        return context


def get_devices():
    con_name_list = subprocess.run('nmcli -g GENERAL.DEVICE dev show', shell=True, capture_output=True, encoding="utf-8"
                                   ).stdout.strip('\n').split('\n\n')
    return_list = {}
    for con_name in con_name_list:
        return_list[con_name] = {}
        con_show_list = subprocess.run(
            'nmcli -f GENERAL,CAPABILITIES,IP4,DHCP4,IP6,DHCP6 dev show "' + con_name + '"',
            shell=True, capture_output=True, encoding="utf-8").stdout.strip('\n').split('\n\n')
        for con_set_str in con_show_list:
            con_set_list = con_set_str.split('\n')
            return_list[con_name]['ipv4address'] = []
            return_list[con_name]['ipv6address'] = []
            for con_set in con_set_list:
                con = con_set.split(': ')
                if 'GENERAL.TYPE:' in con_set:
                    return_list[con_name]['type'] = con[1].strip()
                if 'GENERAL.NM-TYPE:' in con_set:
                    return_list[con_name]['nmtype'] = con[1].strip()
                if 'GENERAL.VENDOR:' in con_set:
                    return_list[con_name]['venddr'] = con[1].strip()
                if 'GENERAL.PRODUCT:' in con_set:
                    return_list[con_name]['product'] = con[1].strip()
                if 'GENERAL.HWADDR:' in con_set:
                    return_list[con_name]['hwaddr'] = con[1].strip()
                if 'GENERAL.NM-TYPE:' in con_set:
                    return_list[con_name]['nmtype'] = con[1].strip()
                if 'GENERAL.MTU:' in con_set:
                    return_list[con_name]['mtu'] = con[1].strip()
                if 'GENERAL.STATE:' in con_set:
                    return_list[con_name]['state'] = con[1].strip()
                    return_list[con_name]['state_num'] = con[1].split('（')[0].strip()
                if 'GENERAL.AUTOCONNECT:' in con_set:
                    return_list[con_name]['dev_autoconnect'] = con[1].strip()
                if 'GENERAL.CONNECTION:' in con_set:
                    return_list[con_name]['connection'] = con[1].strip()
                if 'GENERAL.CON-UUID:' in con_set:
                    return_list[con_name]['conuuid'] = con[1].strip()
                if 'CAPABILITIES.SPEED:' in con_set:
                    return_list[con_name]['capspeed'] = con[1].strip()
                if 'CAPABILITIES.IS-SOFTWARE:' in con_set:
                    return_list[con_name]['capissoftware'] = con[1].strip()
                if 'IP6.ADDRESS[' in con_set:
                    return_list[con_name]['ipv6address'].append(con[1].strip())
                if 'IP4.ADDRESS[' in con_set:
                    return_list[con_name]['ipv4address'].append(con[1].strip())
    return return_list


def get_cons():
    get_con_name_list = subprocess.run(
        'nmcli -g name con show', shell=True, capture_output=True, encoding='utf-8').stdout.strip('\n').split('\n')
    get_con_type_list = subprocess.run(
        'nmcli -f uuid,type con show', shell=True, capture_output=True, encoding='utf-8').stdout.strip('\n').split('\n')
    del get_con_type_list[0]
    get_con_list = subprocess.run(
        'nmcli -g uuid,type,autoconnect,device,state,filename,active con show',
        shell=True, capture_output=True, encoding='utf-8'
    ).stdout.strip('\n').split('\n')

    base_list = {}
    i = 0
    for con in get_con_list:
        con_base = con.split(":")
        base_list[con_base[0]] = {
                'name': get_con_name_list[i].replace('\\', ''), 'uuid': con_base[0], 'autoconnect': con_base[2],
                'device': con_base[3] if con_base[3] else '', 'constate': con_base[4] if con_base[4] else '',
                'filename': con_base[5], 'active': con_base[6]
            }
        for con_type_value in get_con_type_list:
            con_type_list = con_type_value.strip().split('  ')
            con_uuid = con_type_list[0].strip()
            con_type = con_type_list[1].strip()
            if con_base[0] == con_uuid:
                base_list[con_base[0]]['type'] = con_type
        i = i + 1

    return_list = {}
    for uuid, info in base_list.items():
        con_show = subprocess.run(
            'nmcli con show "' + uuid + '"', shell=True, capture_output=True, encoding='utf-8'
        ).stdout.strip().split('\n')

        return_list[uuid] = info
        return_list[uuid]['ipv4addr'] = ''
        return_list[uuid]['ipv4dnsm'] = ''
        return_list[uuid]['ipv4address'] = []
        return_list[uuid]['ipv6address'] = []
        return_list[uuid]['macaddress'] = ''
        return_list[uuid]['ipv4dns'] = []

        for con_str in con_show:
            str_list = con_str.split(': ')
            if len(str_list) == 2:
                name_str = str_list[0] + ':'
                if 'connection.id:' in name_str:
                    return_list[uuid]['id'] = str_list[1].replace(' ', '')
                if 'GENERAL.DEVICE:' in name_str:
                    return_list[uuid]['device'] = str_list[1].replace(' ', '')
                if 'ipv4.method:' in name_str:
                    return_list[uuid]['ipv4method'] = str_list[1].replace(' ', '')
                    return_list[uuid]['ipv4method_cn'] = '-'
                    if return_list[uuid]['ipv4method'] == 'auto':
                        return_list[uuid]['ipv4method_cn'] = '自动(DHCP)'
                    if return_list[uuid]['ipv4method'] == 'manual':
                        return_list[uuid]['ipv4method_cn'] = '手动'
                if 'ipv4.addresses:' in name_str:
                    return_list[uuid]['ipv4'] = str_list[1].replace(' ', '').split(', ')
                if 'ipv6.method:' in name_str:
                    return_list[uuid]['ipv6method'] = str_list[1].replace(' ', '')
                    return_list[uuid]['ipv6method_cn'] = '-'
                    if return_list[uuid]['ipv6method'] == 'auto':
                        return_list[uuid]['ipv6method_cn'] = '自动(DHCP)'
                    if return_list[uuid]['ipv6method'] == 'manual':
                        return_list[uuid]['ipv6method_cn'] = '手动'
                if 'ipv4.addresses:' in name_str:
                    return_list[uuid]['ipv4addr'] = str_list[1].strip()
                if 'ipv4.dns:' in name_str:
                    return_list[uuid]['ipv4dnsm'] = str_list[1].strip()
                if 'IP4.ADDRESS[' in name_str:
                    return_list[uuid]['ipv4address'].append(str_list[1].strip())
                if 'IP6.ADDRESS[' in name_str:
                    return_list[uuid]['ipv6address'].append(str_list[1].strip())
                if 'connection.type:' in name_str:
                    return_list[uuid]['connectiontype'] = str_list[1].strip()
                if '.mac-address:' in name_str:
                    return_list[uuid]['macaddress'] = str_list[1].strip()
                if 'IP4.GATEWAY:' in name_str:
                    return_list[uuid]['ipv4gateway'] = str_list[1].strip()
                if 'IP4.DNS[' in name_str:
                    return_list[uuid]['ipv4dns'].append(str_list[1].strip())

    return return_list


def reload_network():
    return subprocess_run(subprocess, 'systemctl restart network ')


def up_connection(conn_name):
    return subprocess_run(subprocess, f'nmcli connection up {conn_name}')


class DeviceListView(NetworkMixin, TemplateView):
    template_name = 'system_network/device_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '网络管理'
        context['name'] = self.request.GET.get('name')

        context['devices'] = {}
        devices = get_devices()
        get_conn = get_cons()
        for k, v in devices.items():
            if v['conuuid'] in get_conn:
                v.update(get_conn[v['conuuid']])
            context['devices'][k] = v
        return context


class DeviceAutoConnectView(NetworkMixin, RedirectView):

    def get(self, request, *args, **kwargs):
        name = self.request.GET.get('name')
        action = kwargs['action']
        conuuid = kwargs['uuid']
        status = ''
        exec_statement = ''
        if action == 'disabled':
            exec_statement = f'nmcli connection modify {conuuid} connection.autoconnect no'
            status = '禁用网络自动连接'
        if action == 'enabled':
            exec_statement = f'nmcli connection modify {conuuid} connection.autoconnect yes'
            status = '启用网络自动连接'
        if action == 'enableddev':
            exec_statement = f'nmcli device connect {name}'
            status = '启用网络接口设备'

        run_end = subprocess_run(subprocess, exec_statement)
        if run_end.returncode != 0:
            messages.warning(request, f'{status} {name} 操作失败！{run_end.stdout}{run_end.stderr}')
        else:
            reload_network()
            messages.success(request, f'{status} {name}  操作完成!')
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse('module_system:system_network:device_list') + '?name=' + self.request.GET.get('name')


class Ipv4EditView(NetworkMixin, FormView):
    form_class = Ipv4Form
    template_name = 'system_network/ipv4_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '配置ipv4'
        context['breadcrumb'] = [
            {
                'title': '网络配置',
                'href': reverse_lazy('module_system:system_network:device_list') + f"?name={self.kwargs['name']}",
                'active': False
            },
            {'title': '配置ipv4', 'href': '', 'active': True},
        ]
        return context

    def get_initial(self):
        self.initial = super().get_initial()
        conn_info = get_cons()[self.kwargs['uuid']]
        self.initial['ipv4method'] = conn_info['ipv4method']
        ipv4addr = conn_info['ipv4address'][0].split('/')
        self.initial['ipv4addr'] = ipv4addr[0]
        self.initial['netmask'] = ipv4addr[1]
        self.initial['ipv4gateway'] = conn_info['ipv4gateway']
        self.initial['ipv4dns'] = ','.join(conn_info['ipv4dns'])
        return self.initial.copy()

    def form_valid(self, form):
        name = self.kwargs['name']
        ipv4method = form.cleaned_data.get('ipv4method')
        ipv4addr = form.cleaned_data.get('ipv4addr')
        netmask = form.cleaned_data.get('netmask')
        ipv4getway = form.cleaned_data.get('ipv4gateway').strip()
        ipv4dns = form.cleaned_data.get('ipv4dns').replace(' ', '').replace('，', ',').strip()

        exec_statement = ''
        if ipv4method == 'manual':
            exec_statement = (f'nmcli connection modify {name} ipv4.method {ipv4method} '
                              f'ipv4.addresses {ipv4addr}/{netmask}')
            if ipv4getway:
                exec_statement += f' ipv4.gateway {ipv4getway}'
            if ipv4dns:
                exec_statement += f' ipv4.dns {ipv4dns}'

        if ipv4method == 'auto':
            exec_statement = f'nmcli connection modify {name} ipv4.method auto'

        exec_result = subprocess_run(subprocess, exec_statement)
        if exec_result.returncode == 0:
            up_connection(name)
            messages.success(self.request, '编辑网络状态完成！')
            self.success_url = reverse('module_system:system_network:device_list') + f'?name={name}'
        else:
            messages.warning(self.request, f'网络状态编辑失败！{exec_result.stdout}{exec_result.stderr}')
            self.success_url = reverse(
                'module_system:system_network:ipv4_edit',
                kwargs={'name': name, 'uuid': self.kwargs['uuid']}
            )
        return super().form_valid(form)
