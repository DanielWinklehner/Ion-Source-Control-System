import json
from flask import *

def devices_as_html(devstr):

    html_header = '''
    <html>
        <head>
            <link rel="stylesheet" type="text/css" href="{}">
        </head>
        <body>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Driver</th>
                    <th>Port</th>
                </tr>
    '''.format(url_for('static',filename='styles/style.css'))

    html_footer = '''
            </table>
        </body>
    </html>
    '''

    devdict = json.loads(devstr)

    htmlstr = html_header 

    for dev_id, dev_info in devdict.iteritems():
        devstr = '            <tr>\n'
        devstr += '                <th>{}</th>\n'.format(dev_id)
        for key, val in dev_info.iteritems():
            devstr += '                <th>{}</th>\n'.format(val)

        devstr += '            </tr>\n'
        htmlstr += devstr

    htmlstr += html_footer

    return htmlstr

if __name__ == '__main__':
    samplestr = '''
    {"954323138373513060D0": {"identifyer": "Arduino", "port": "/dev/ttyACM2"}, "3596460": {"identifyer": "Teensy", "port": "/dev/ttyACM4"}, "95433343733351507011": {"identifyer": "Arduino", "port": "/dev/ttyACM0"}, "954323138373519002A2": {"identifyer": "Arduino", "port": "/dev/ttyACM1"}, "FTJRNRWQ": {"identifyer": "RS485", "port": "/dev/ttyUSB0"}, "95433343733351502071": {"identifyer": "Arduino", "port": "/dev/ttyACM3"}}
    '''

    print devices_as_html(samplestr)
