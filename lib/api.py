from gevent import monkey; monkey.patch_all()
import gevent
import importlib
import os
import time
from urlparse import urlparse

def scan(script, target_ip, target_port, productname={}):
    result = []
    g_list = []
    for ones in script:
        if os.path.isdir('script/' + ones):
            for onef in os.listdir('script/' + ones):
                if '.py' in onef and '.pyc' not in onef and 't.py' != onef and '__init__.py' != onef:
                    doc = 'scrpit.' + ones + '.' + onef[:-3]
                    mod = importlib.import_module('script.' + ones + '.' + onef[:-3])
                    g_list.append(gevent.spawn(g_scan, doc, result, mod, target_ip, target_port, productname))
        else:
            if '.py' in ones and '.pyc' not in ones and 't.py' != ones and '__init__.py' != ones:
                ones = ones.replace('/', '.')
                doc = 'scrpit.' + ones[:-3]
                mod = importlib.import_module('script.' + ones[:-3])
                g_list.append(gevent.spawn(g_scan, doc, result, mod, target_ip, target_port, productname))
    gevent.joinall(g_list)
    return result
    
def g_scan(doc, result, mod, target_ip, target_port, productname={}):
    g_result = {}
    print '[*]', doc, 'testing...'
    if target_port != '':
        g_result = mod.P().verify(ip=target_ip, port=target_port, productname=productname)
    else:
        g_result = mod.P().verify(ip=target_ip, productname=productname)
    result.append(g_result)
    if g_result['result'] == True:
        print '[!]', doc
    return

def out(output, result):
    wresult = '======================= pocmap v1.0 =======================\n'
    for oner in result:
        if oner['result'] == True:
            for k, v in oner['VerifyInfo'].iteritems():
                try:
                    wresult += '{k}: {v}\n'.format(k=str(k), v=str(v))
                except:
                    print '[output error]', k, v
            wresult += '-----------------------------------------------------------\n'
    f = open(output, 'w')
    f.write(wresult)
    f.close()
    return

def handle_url(url):
    url = urlparse(url)
    if ':' in url.netloc:
        target_ip = str(url.netloc.split(':')[0])
        target_port = str(url.netloc.split(':')[1])
    else:
        target_ip = str(url.netloc)
        if str(url.scheme) == 'https':
            target_port = '443'
        else:
            target_port = '80'
    path = url.path
    return target_ip, target_port, path

def handle_target(target):
    target_ip = ''
    target_port = ''
    if ':' in target:
        target_ip = target.split(':')[0]
        target_port = target.split(':')[1]
    else:
        target_ip = target
    return target_ip, target_port
