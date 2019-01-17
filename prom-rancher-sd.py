#!/usr/bin/env python3

# Copyright 2016 Daniel Dent (https://www.danieldent.com/)
# Copyright 2016 Virgil Chereches (virgil.chereches@gmx.net)
# Copyright 2019 Dzmitry Akunevich (dzmitry@akunevich.com)


import urllib.parse
import urllib.request
from urllib.error import URLError, HTTPError
import os, sys, re, time, shutil
import json, logging


outputFolder = os.getenv('OUTPUT_FOLDER', '/prom-rancher-sd-data').rstrip('/')
discoveryTime = os.getenv('DISCOVERY_TIME', '5')

JobRegex = re.compile(os.getenv('JOB_REGEX'.rstrip()))


def get_current_metadata_entry(entry):
    headers = {
        'User-Agent': "prom-rancher-sd/0.1",
        'Accept': 'application/json'
    }

    try:
        req = urllib.request.Request('http://rancher-metadata.rancher.internal/2016-07-29/%s' % entry, headers=headers)
        logger.debug('Sent request to metadata service')
    except HTTPError as e:
        logger.error('Error code: %s', e.code)
    except URLError as e:
        logger.error('Reason: %s', e.reason)

    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf8 '))
    
    logger.debug('Got rancher metadata')


def is_monitored_service(service):
    logger.debug('Processing % service', service['name'])
    # don't monitor container's that don't have IP yet

    if not 'primary_ip' in service:
        logger.debug('%s has no primary_ip', service['name'])
        return False
    
    if not service['primary_ip']:
        logger.debug('%s has no primary_ip assigned', service['name'])
        return False

    if 'com.prometheus.job_name' in service['labels']:
        logger.debug('%s has job_name set', service['labels']['com.prometheus.job_name'])
        mo = JobRegex.search(service['labels']['com.prometheus.job_name'])
        if mo:
            logger.debug('Job_filter: %s succeeded', os.getenv('JOB_REGEX'.rstrip()))
            logger.debug('Filtered job_name %s', service['labels']['com.prometheus.job_name'])
            return 'labels' in service and mo.group(0) in service['labels']['com.prometheus.job_name']
    else:
        return 'labels' in service and 'com.prometheus.job_name' in service['labels']
    logger.info('%s service processed', service['service_name'])


def monitoring_config(service):
    logger.info('%s config created', service['service_name'])
    return {
        "targets": [service['primary_ip'] + ':' + (service['labels']['com.prometheus.port'] if 'com.prometheus.port' in service['labels'] else '8083') ],
        "labels": {
            'instance': None,
            '__metrics_path__': service['labels']['com.prometheus.metricspath'] if 'com.prometheus.metricspath' in service['labels'] else '/metrics',
            '__meta_rancher_container_name': service['name'],
            '__meta_rancher_service_name': service['service_name'],
            '__meta_rancher_stack': service['stack_name'],
            '__meta_rancher_job_name': service['labels']['com.prometheus.job_name']
        },
       "host-uuid": service['host_uuid']
    }


def get_hosts_dict(hosts):
   return { x['uuid']:x['hostname'] for x in hosts }


def get_monitoring_config():
    return list(map(monitoring_config, filter(is_monitored_service, get_current_metadata_entry('containers'))))


def enrich_dict(dictionary,hostdict):
    assert 'host-uuid' in dictionary
    assert dictionary['host-uuid'] in hostdict
    hostname = hostdict[dictionary['host-uuid']]
    dictionary['labels']['instance']=hostname
    dictionary.pop('host-uuid',None)
    return dictionary


def write_config_file(filename,get_config_function):
    hostdict = get_hosts_dict(get_current_metadata_entry('hosts'))
    configlist = get_config_function()
    newconfiglist = [ enrich_dict(x,hostdict) for x in configlist ]
    tmpfile = filename+'.temp'
    
    try:
        with open(tmpfile, 'w') as config_file:
            print(json.dumps(newconfiglist, indent=2),file=config_file)
    except OSError as e:
        logger.error('OS error: {0}'.format(e))
    except:
        logger.error('Unexpected error: %s', sys.exc_info()[0])
        raise    
    shutil.move(tmpfile,filename)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.setLevel(os.environ.get('LOGLEVEL', 'INFO'))
    format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(format)
    logger.addHandler(ch)

    logger.info('Log started')

    while True:
        time.sleep(int('{0}'.format(discoveryTime)))
        logger.info('Start processing')
        write_config_file('{0}/rancher.json'.format(outputFolder),get_monitoring_config)
        logger.info('Service configuration written')
