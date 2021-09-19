import requests, urllib3, json
import pandas as pd
urllib3.disable_warnings()

api_version = { '8.0.0' : '3',
                '8.0.1' : '4',
                '8.1.0' : '5',
                '8.1.1' : '6',
                '8.1.2' : '6',
                '8.1.3' : '6',
                '8.2.0' : '7',
                '8.2.1' : '8',
                '8.2.2' : '9',
                '9.0.0' : '10',
                '9.1.0' : '11',
                '9.2.0' : '12' }

class isilon_session:
    def __init__(self, host, username, password, port='8080'):
        self.session = requests.Session()
        self.cookieJar = requests.cookies.RequestsCookieJar()
        self.headers = {'Content-Type': 'application/json'}
        self.data = '{"username" : "' + username + '", "password" : "' + password +'", "services" : ["platform", "namespace"]}'
        self.base = 'https://' + host + ':' + port
        
        self.platform = '/platform/3'
        self.auth_url = self.platform + '/auth/id'

        get_session_url = self.base + '/session/1/session'
        self.get_auth = self.base + self.auth_url

        self.r_session = self.session.post(get_session_url, verify=False, data=self.data, headers=self.headers, cookies=self.cookieJar)
        
        self.headers['X-CSRF-Token'] = self.r_session.headers['Set-Cookie'].split('; ')[4].split(', ')[1].split('=')[1]
        self.headers['Cookie'] = self.r_session.headers['Set-Cookie'].split(';')[0]
        self.headers['Origin'] = self.base

        # Get onefs version for appropriate api version
        response = self.session.get(self.base + self.platform  + '/cluster/version', verify=False, data=self.data, headers=self.headers, cookies=self.cookieJar)
        onefs = json.loads(response.text)['nodes'][0]['release'][1:][:5]
        self.platform = '/platform/' + api_version[onefs]

    def call(self, type, path, data='{}'):
        if type == 'POST':
            return self.session.post(self.base + self.platform + path, verify=False, data=data, headers=self.headers, cookies=self.cookieJar)
        elif type == 'GET':
            return self.session.get(self.base + self.platform + path, verify=False, data=data, headers=self.headers, cookies=self.cookieJar)
        else:
            return 'Error'

# Return a dictionary with all available access zones.
def parse_zones(sess):
    response = sess.call('GET', '/zones')
    jr = json.loads(response.text)
    z_dict = {}
    for z in jr['zones']:
        z_dict[z['id']] = str(z['zone_id'])
    return z_dict

# Create SMB Share
def create_smb_share(sess, zone_name, **kwargs):
    zones = parse_zones(sess)
    return sess.call('POST', '/protocols/smb/shares?zid=' + zones[zone_name], json.dumps(kwargs))

def main():
    rdcisilon = isilon_session('10.54.162.150', 'root', 'a')
    response = create_smb_share(rdcisilon, 'System', name='resttest6', path='/ifs/data/resttest')
    
    if response.status_code > 201:
        print('Operation Failed with:', json.loads(response.text)['errors'][0]['code'] + ' - ' + json.loads(response.text)['errors'][0]['message'] )
    else:
        print('Done!')
    return response


if __name__ == '__main__':
    main()