#!/usr/bin/env python2.7

import argparse, os, re, shutil

def getArgs():
    parser = argparse.ArgumentParser(description="Manage CouchDB instances for Jenkins Executors")
    parser.add_argument('--templates', help='Path to CouchDB template directories', required=True)
    parser.add_argument('--workspace', help='Path to Jenkins workspace', required=True)
    parser.add_argument('--executor', type=int, help='Jenkins executor ID', required=True)
    parser.add_argument('--response', help='Name of the response file template to use for LR configuration.', default='lr_config_response.txt')
    return parser.parse_args()


def getEnvExtra(args):
    couchdb_instance = '%(workspace)s/couchdb' % {"workspace": re.sub(os.sep+'+$', '', args.workspace) }
    gnupg_home = '%(workspace)s/gnupg' % {"workspace": re.sub(os.sep+'+$', '', args.workspace) }
    return {
        'httpd_bind_address': '127.0.0.1',
        'httpd_port': 6984 + args.executor,
        'couchdb_instance': couchdb_instance,
        'lr_config_response_tmpl': args.response,
        'lr_config_response': os.path.join(couchdb_instance, args.response),
        'couchdb_local_ini': os.path.join(couchdb_instance, 'etc', 'couchdb', 'local.ini'),
        'extra_env': os.path.join(couchdb_instance, 'couch_env.sh'),
        'gnupg_home': gnupg_home
    }

def writeEnvVars(vars, prefix="jenkins"):
    extra = getEnvExtra(vars)
    with open(extra['extra_env'], "w+") as f:
        for key, val in extra.items():
            f.write('%(prefix)s_%(key)s=%(val)s\n'%{'prefix':prefix, 'key':key, 'val':val})
        f.close()


def merge_template(file, vars={}, **kwvars):
    vars.update(kwvars);
    return open(file, "r").read() % vars



def make_lr_config_response(args):
    env = getEnvExtra(args)
    lr_config = os.path.join(args.templates, env['lr_config_response_tmpl'])
    httpd_bind_address = env['httpd_bind_address']
    httpd_port = env['httpd_port']

    return merge_template(lr_config, 
        httpd_port=httpd_port, 
        httpd_bind_address=httpd_bind_address,
        gnupg_home=env['gnupg_home'],
        workspace=args.workspace)

def write_lr_config_response(args, contents):
    env = getEnvExtra(args)
    couchdb_instance = env['couchdb_instance']

    with open(os.path.join(couchdb_instance, env['lr_config_response_tmpl']), 'w+') as f:
        f.write(contents.encode('utf-8'))
        f.close()

def make_couchdb_local_ini(args):
    env = getEnvExtra(args)
    couchdb_instance = env['couchdb_instance']
    httpd_bind_address = env['httpd_bind_address']
    httpd_port = env['httpd_port']

    local_ini = os.path.join(args.templates, 'etc', 'couchdb', 'local.ini')
    return merge_template(local_ini, 
        couchdb_instance=couchdb_instance, 
        httpd_port=httpd_port, 
        httpd_bind_address=httpd_bind_address)

def write_couchdb_local_ini(args, contents):
    couchdb_instance = '%(workspace)s/couchdb' % {"workspace": re.sub(os.sep+'+$', '', args.workspace) }

    etc_couchdb = os.path.join(couchdb_instance, 'etc', 'couchdb')
    with open(os.path.join(etc_couchdb, 'local.ini'), 'w+') as f:
        f.write(contents.encode('utf-8'))
        f.close()

def clone_couchdb_templates(arg):
    src = args.templates
    dst = '%(workspace)s/couchdb' % {"workspace": re.sub(os.sep+'+$', '', args.workspace) }

    # try:
    #     os.makedirs(dst)
    # except OSError as e:
    #     if e.errno != 17:
    #         raise e

    try:
        shutil.copytree(src, dst)
    except OSError as e:
        if e.errno != 17:
            raise e






if __name__ == '__main__':
    args = getArgs()
    clone_couchdb_templates(args)
    local_ini = make_couchdb_local_ini(args)
    write_couchdb_local_ini(args, local_ini)
    response_file = make_lr_config_response(args)
    write_lr_config_response(args, response_file)
    writeEnvVars(args)



