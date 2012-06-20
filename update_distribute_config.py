#!/usr/bin/env python2.7

import argparse, os, re, shutil, ConfigParser

INI_SECTION = 'couch_info'
SERVER = 'server'

def getArgs():
    parser = argparse.ArgumentParser(description="Manage LR Distribute Test configuration for Jenkins Executors")
    parser.add_argument('--workspace', help='Path to Jenkins workspace', required=True)
    parser.add_argument('--executor', type=int, help='Jenkins executor ID', required=True)
    parser.add_argument('--config', help='Path to Distribute Test config directory', default='/LearningRegistry/LR/lr/tests/functional/distribute/config')
    return parser.parse_args()

def getEnvExtra(vars):
    couchdb_instance = '%(workspace)s/couchdb' % {"workspace": re.sub(os.sep+'+$', '', args.workspace) }
    return {
        'httpd_bind_address': '127.0.0.1',
        'httpd_port': 6984 + args.executor,
        'couchdb_instance': couchdb_instance,
        'couchdb_local_ini': os.path.join(couchdb_instance, 'etc', 'couchdb', 'local.ini'),
        'distribute_cfg':os.path.join(args.workspace, args.config),
        'extra_env': os.path.join(couchdb_instance, 'couch_env.sh')

    }

def process(vars):
    env = getEnvExtra(vars)
    for c in os.listdir(env['distribute_cfg']):
        config = ConfigParser.ConfigParser()
        cfg_file = os.path.join(env['distribute_cfg'], c)
        config.read(cfg_file)
        couch_url = 'http://%(httpd_bind_address)s:%(httpd_port)s' % env
        if config.has_section(INI_SECTION):
            config.set(INI_SECTION, SERVER, couch_url)
            config.write(open(cfg_file, "w"))


if __name__ == '__main__':
    args = getArgs()
    process(args)
