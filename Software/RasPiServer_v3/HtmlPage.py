import json
from flask import *

def devices_as_html(_devstr, querystr=''):

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
                    <th>Read Channels</th>
                </tr>
    '''.format(url_for('static',filename='styles/style.css'))

    html_footer = '''
            </table>
        </body>
    </html>
    '''

    htmlstr = html_header 
    devstr = ''
    
    try:
        devdict = json.loads(_devstr)
        querydict = json.loads(querystr)
    except:
        return _devstr, querystr

    for dev_id, dev_info in devdict.iteritems():
        deventries = []
        deventries.append(dev_id)
        for key, val in dev_info.iteritems():
            deventries.append(val)

        deventries.append(', '.join([ch_name for ch_name, _  in querydict[dev_id].iteritems()]))

        devstr += tableify(deventries)

    htmlstr += devstr
        
    htmlstr += html_footer
    return htmlstr

def tableify(entries=()):
    outstr = '<tr>\n'

    for entry in entries:
        outstr += '<th>{}</th>\n'.format(entry)

    outstr += '</tr>\n'

    return outstr

if __name__ == '__main__':
    samplestr = '''
    {"954323138373513060D0": {"identifyer": "Arduino", "port": "/dev/ttyACM2"}, "3596460": {"identifyer": "Teensy", "port": "/dev/ttyACM4"}, "95433343733351507011": {"identifyer": "Arduino", "port": "/dev/ttyACM0"}, "954323138373519002A2": {"identifyer": "Arduino", "port": "/dev/ttyACM1"}, "FTJRNRWQ": {"identifyer": "RS485", "port": "/dev/ttyUSB0"}, "95433343733351502071": {"identifyer": "Arduino", "port": "/dev/ttyACM3"}}
    '''

    print devices_as_html(samplestr)
