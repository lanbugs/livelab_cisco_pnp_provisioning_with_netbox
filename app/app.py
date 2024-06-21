from flask import Flask, request, Response, render_template
from dynaconf import FlaskDynaconf
from helper import parse_cisco_pnp, parse_pnp_xml_response
from netbox import check_device_existing, add_device, get_config, check_device_staged, set_device_status_active
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)
FlaskDynaconf(app, envvar_prefix='APP')


@app.route("/pnp/HELLO")
def hello():
    """
    This endpoint answers to HELLO requests of Cisco devices with 200/OK
    :return:
    """
    return "", 200


@app.route("/pnp/WORK-REQUEST", methods=["POST"])
def work_request():
    """
    Process a POST request for the "/pnp/WORK-REQUEST" route.
    """
    data = parse_cisco_pnp(request.data)

    # Check if device is present in Netbox
    if check_device_existing(data['sn']) is False:
        add_device(data['sn'], data['pid'], request.remote_addr)

    # Check if device is in mode staging in Netbox
    if check_device_staged(data['sn']):
        if app.config.SEC_CONFIG is True:
            serializer = URLSafeTimedSerializer(app.config.SEC_KEY)
            token = serializer.dumps(data['sn'])
        else:
            token = data['sn']

        location = f"http://{app.config.PNP_IP}:{app.config.PNP_PORT}/c/{token}"

        return Response(
            render_template(
                "config_upgrade.xml",
                reload_delay = 5,
                udi=data['udi'],
                correlator=data['correlator'],
                location=location
            ), mimetype='application/xml')

    return "", 200


@app.route("/pnp/WORK-RESPONSE", methods=["POST"])
def work_response():
    """
    Process WORK-RESPONSE requests.
    """
    data = parse_pnp_xml_response(request.data)

    if data['success'] == '1':
        set_device_status_active(data['sn'])

    return Response(
        render_template(
            "bye.xml",
            udi=data['udi'],
            correlator=data['correlator']
        ), mimetype='application/xml')


@app.route("/c/<token>")
def return_config(token: str):
    """
    Method to return configuration based on provided token.

    :param token: A string representing the token for retrieving the configuration.
    :return: A Response object containing the configuration in plain text format.
    """
    if app.config.SEC_CONFIG is True:
        try:
            serializer = URLSafeTimedSerializer(app.config.SEC_KEY)
            token = serializer.loads(token, max_age=app.config.SEC_AGE)
        except:
            return Response(status=404)

    return Response(get_config(token), mimetype="text/plain")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=2222, debug=True)
