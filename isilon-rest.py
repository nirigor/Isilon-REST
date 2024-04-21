import socket
import requests, urllib3
urllib3.disable_warnings()

class PowerScale:
    def __init__(self, host, username, password, port='8080'):
        self.host = socket.gethostbyname(host)
        self.base_url = f'https://{self.host}:{port}'
        
        self.session = requests.Session()
        self.cookieJar = requests.cookies.RequestsCookieJar()
        self.headers = { 'Content-Type': 'Application/Json' }
        
        auth_payload = {
            'username' : username,
            'password' : password,
            'services' : ['platform', 'namespace']
        }
        
        response = self.session.post(f'{self.base_url}/session/1/session', verify=False, json=auth_payload, headers=self.headers, cookies=self.cookieJar)
        
        self.headers['X-CSRF-Token'] = response.cookies["isicsrf"]
        self.headers['Cookie'] = f'isisessid={response.cookies["isisessid"]}'
        self.headers['Origin'] = self.base_url
        
        response = self.session.get(f'{self.base_url}/platform/latest', verify=False, json=auth_payload, headers=self.headers, cookies=self.cookieJar)
        latest = response.json()['latest']
        self.platform_url = f'/platform/{latest}'
        
    def __enter__(self):
        return self

    def call(self, method, path, payload={}, params={}):
        url = self.base_url + path if 'namespace' in path else self.base_url + self.platform_url + path
        if method == 'GET':
            return self.session.get(url, verify=False, params=params, headers=self.headers, cookies=self.cookieJar)
        elif method == 'HEAD':
            return self.session.head(url, verify=False, params=params, headers=self.headers, cookies=self.cookieJar)
        elif method == 'DELETE':
            return self.session.delete(url, verify=False, params=params, headers=self.headers, cookies=self.cookieJar)
        elif method == 'POST':
            return self.session.post(url, verify=False, params=params, json=payload, headers=self.headers, cookies=self.cookieJar)
        elif method == 'PUT':
            return self.session.put(url, verify=False, params=params, json=payload, headers=self.headers, cookies=self.cookieJar)
        else:
            self.close()
            raise Exception(f'Method "{method}" is not supported... \nSupported methods are ["GET", "HEAD", "DELETE", "POST", "PUT"]')
    
    def close(self):
        return self.session.delete(f'{self.base_url}/session/1/session', verify=False, headers=self.headers, cookies=self.cookieJar)
    
    def __exit__(self, exc_type, exc_value, traceback):
        return self.close()
