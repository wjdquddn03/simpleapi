# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 OpenStack Foundation
# Copyright 2012 Nebula, Inc.
# Copyright (c) 2012 X.commerce, a business unit of eBay Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from __future__ import absolute_import

import logging

from django.conf import settings
from django.utils.functional import cached_property  # noqa
from django.utils.translation import ugettext_lazy as _

from novaclient import exceptions as nova_exceptions
from novaclient.v2 import client as nova_client
from novaclient.v2.contrib import instance_action as nova_instance_action
from novaclient.v2.contrib import list_extensions as nova_list_extensions
from novaclient.v2 import security_group_rules as nova_rules
from novaclient.v2 import security_groups as nova_security_groups
from novaclient.v2 import servers as nova_servers

from horizon import conf
from horizon.utils import functions as utils
from horizon.utils.memoized import memoized  # noqa

from openstack_dashboard.api import base
from openstack_dashboard.api import network_base


import json
import requests
import six

LOG = logging.getLogger(__name__)


# API static values
INSTANCE_ACTIVE_STATE = 'ACTIVE'
VOLUME_STATE_AVAILABLE = "available"
DEFAULT_QUOTA_NAME = 'default'



class NovaUsage(base.APIResourceWrapper):
    """Simple wrapper around contrib/simple_usage.py."""

    _attrs = ['start', 'server_usages', 'stop', 'tenant_id',
             'total_local_gb_usage', 'total_memory_mb_usage',
             'total_vcpus_usage', 'total_hours', '']

#    _attrs = ['tenant_id', 'disk_gb' , 'disk_gb_hour', 'memory_mb',
#            'vcpus', 'memory_mb_hour', 'active_instance', 'vcpus_hour']

#    def get_summary(self):
#        return {'instances': getattr(self,"active_instance", 0),
#                'memory_mb': getattr(self,"memory_mb", 0),
 #               'vcpus': getattr(self, "vcpus_usage", 0),
  #              'vcpu_hours': self.vcpu_hours ,
   #             'local_gb': getattr(self,"local_gb", 0),
    #            'disk_gb_hours': getattr(self,"disk_gb_hour", 0),
     #           'memory_mb_hours': getattr(self,"memory_mb_hour", 0)}  
    
    def get_summary(self):
        return {'instances': self.total_active_instances,
                'memory_mb': self.memory_mb,
                'vcpus': getattr(self, "total_vcpus_usage", 0),
                'vcpu_hours': self.vcpu_hours,
                'local_gb': self.local_gb,
                'disk_gb_hours': self.disk_gb_hours,
                'memory_mb_hours': self.memory_mb_hours}


    @property
    def total_active_instances(self):
#        return sum(1 for s in self.server_usages if s['ended_at'] is None)
        return getattr(self, "active_instance", 0)
    
    @property
    def vcpus(self):
#        return sum(s['vcpus'] for s in self.server_usages
#                   if s['ended_at'] is None)
        return getattr(self, "vcpus", 0)

    @property
    def vcpu_hours(self):
        return getattr(self, "total_hours", 0)

    @property
    def local_gb(self):
#        return sum(s['local_gb'] for s in self.server_usages
#                   if s['ended_at'] is None)
        return getattr(self, "disk_gb", 0)

    @property
    def memory_mb(self):
#        return sum(s['memory_mb'] for s in self.server_usages
#                   if s['ended_at'] is None)
        return getattr(self, "memory_bm", 0)
        
    @property
    def disk_gb_hours(self):
#        return getattr(self, "total_local_gb_usage", 0)
        return getattr(self, "disk_gb_hour", 0)

    @property
    def memory_mb_hours(self):
#        return getattr(self, "total_memory_mb_usage", 0)
        return getattr(self, "memory_mb_hours", 0)


class SimpleNovaclient(object):
    def __init__(self,info):
        self._add_details(info)


    def _add_details(self,info):
        for(k,v) in six.iteritems(info):
            try:
                setattr(self,k,v)
            except AttributeError:
                pass

def usage_list(request, start, end):
    method = 'GET'
    url = 'http://localhost:5001/admin/overview'
#    url = 'http://localhost:5001/'
    resp_func = requests.request
    resp = resp_func(method,url)
    body = json.loads(resp.text)
    data = body['projects']
#    data = body['tenant_usages']

    _tmp = [SimpleNovaclient(t) for t  in data]
    return [NovaUsage(u) for u in _tmp]
#    return [NovaUsage(u) for u in data]


#def usage_list(request, start, end):
#    return [NovaUsage(u) for u in
#            novaclient(request).usage.list(start, end, True)]


