import xml.etree.ElementTree as ET
from xml.dom import minidom


def parse_cisco_pnp(xml_string):
    # Parse the XML string
    root = ET.fromstring(xml_string)

    # Define namespaces
    namespaces = {
        'pnp': 'urn:cisco:pnp',
        'info': 'urn:cisco:pnp:work-info'
    }

    # Extract the root element attributes
    pnp_version = root.attrib.get('version')
    udi = root.attrib.get('udi')

    # Extract PID, VID, and SN from the udi
    pid, vid, sn = None, None, None
    if udi:
        parts = udi.split(',')
        for part in parts:
            if part.startswith('PID:'):
                pid = part.split(':')[1]
            elif part.startswith('VID:'):
                vid = part.split(':')[1]
            elif part.startswith('SN:'):
                sn = part.split(':')[1]

    # Find the info element
    info_elem = root.find('info:info', namespaces)
    correlator = info_elem.attrib.get('correlator')

    # Find the deviceId element
    device_id_elem = info_elem.find('info:deviceId', namespaces)
    device_udi = device_id_elem.find('info:udi', namespaces).text
    hostname = device_id_elem.find('info:hostname', namespaces).text
    auth_required = device_id_elem.find('info:authRequired', namespaces).text
    via_proxy = device_id_elem.find('info:viaProxy', namespaces).text
    security_advise = device_id_elem.find('info:securityAdvise', namespaces).text

    # Create a dictionary to hold the extracted data
    parsed_data = {
        'pnp_version': pnp_version,
        'udi': udi,
        'pid': pid,
        'vid': vid,
        'sn': sn,
        'correlator': correlator,
        'device_udi': device_udi,
        'hostname': hostname,
        'auth_required': auth_required,
        'via_proxy': via_proxy,
        'security_advise': security_advise
    }

    return parsed_data


def parse_pnp_xml_response(xml_data):
    # Definieren des Namespaces
    namespaces = {
        'pnp': 'urn:cisco:pnp',
        'config-upgrade': 'urn:cisco:pnp:config-upgrade'
    }

    root = ET.fromstring(xml_data)

    udi = root.attrib.get('udi')

    # Extract PID, VID, and SN from the udi
    pid, vid, sn = None, None, None
    if udi:
        parts = udi.split(',')
        for part in parts:
            if part.startswith('PID:'):
                pid = part.split(':')[1]
            elif part.startswith('VID:'):
                vid = part.split(':')[1]
            elif part.startswith('SN:'):
                sn = part.split(':')[1]

    parsed_data = {
        'pid': pid,
        'vid': vid,
        'sn': sn,
        'udi': udi
    }

    response = root.find('config-upgrade:response', namespaces)
    if response is not None:
        parsed_data['success'] = response.attrib.get('success', None)
        parsed_data['correlator'] = response.attrib.get('correlator', None)
    else:
        parsed_data['success'] = None
        parsed_data['correlator'] = None

    return parsed_data
