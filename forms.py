from django import forms
from appcommon.forms import FormBase


class Ipv4Form(FormBase):
    ipv4method = forms.CharField(
        label='IPv4模式',
        widget=forms.Select(
            choices=(('auto', '自动(DHCP)'), ('manual', '手动')),
            attrs={'class': 'form-control', 'ipv4method': '', 'lay-filter': "ipv4method-filter"}
        )
    )
    ipv4addr = forms.CharField(
        label='IPv4地址', required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'lay-verify': 'ipv4check'})
    )
    netmask = forms.IntegerField(
        label='子网掩码', required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'lay-verify': 'ipv4check'})
    )
    ipv4gateway = forms.CharField(label='网关', required=False,
                          widget=forms.TextInput(attrs={'class': 'form-control', 'lay-verify': 'gw4'})
                          )
    ipv4dns = forms.CharField(
        label='DNS', required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'lay-verify': 'dns'})
    )
