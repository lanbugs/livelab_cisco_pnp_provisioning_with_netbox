import pynetbox
import requests
from dynaconf import Dynaconf
import ipaddress

# Config
config = Dynaconf(envvar_prefix='APP')

# Init Netbox
session = requests.Session()
session.verify = False
nb = pynetbox.api(config.NETBOX_URL, token=config.NETBOX_TOKEN)
nb.http_session = session


def ip_in_subnet(ip, subnet):

    ip_addr = ipaddress.ip_address(ip)
    subnet_net = ipaddress.ip_network(subnet, strict=False)
    return ip_addr in subnet_net


def check_device_existing(sn):
    if nb.dcim.devices.count(serial=sn) == 0:
        return False
    return True


def undefined_site():
    if nb.dcim.sites.count(name='Undefined') == 0:
        site = nb.dcim.sites.create(
            name='Undefined',
            slug='undefined'
        )
        return site.id
    else:
        return nb.dcim.sites.get(name='Undefined').id


def undefined_device_role():
    if nb.dcim.device_roles.count(name='Undefined') == 0:
        return nb.dcim.device_roles.create(
            name='Undefined',
            slug='undefined'
        ).id
    else:
        return nb.dcim.device_roles.get(name='Undefined').id


def determine_site(ip):
    """ try to determine the site based on the IP address if not possible site Undefined will be used """
    subnets = nb.ipam.prefixes.filter(tag="pnp_network")

    for subnet in subnets:
        if ip_in_subnet(ip, subnet.prefix):
            return subnet.site.id

    return undefined_site()


def add_device(sn, pid, ip):
    device = nb.dcim.devices.create(
        name=sn,
        serial=sn,
        status='planned',
        site=determine_site(ip),
        device_type=nb.dcim.device_types.get(part_number=pid).id,
        role=undefined_device_role(),
    )
    return device


def check_device_staged(sn):
    device = nb.dcim.devices.get(serial=sn)
    if device.status.value == 'staged':
        return True
    return False


def get_config(serial):
    device = nb.dcim.devices.get(serial=serial)

    headers = {
        "Authorization": f"Token {config.NETBOX_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(f"{config.NETBOX_URL}/api/dcim/devices/{device.id}/render-config/", headers=headers, verify=False)

    if response.status_code == 200:
        return response.json()['content']
    else:
        return ""


def set_device_status_active(sn):
    device = nb.dcim.devices.get(serial=sn)
    device.status = 'active'
    device.save()
    return device