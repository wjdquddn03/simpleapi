
from __future__ import absolute_import

import logging

from django.conf import settings
from django.utils.functional import cached_property  # noqa
from django.utils.translation import ugettext_lazy as _

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

    _attrs = ['tenant_id', 'project_name',
              'total_local_gb_usage', 'total_memory_mb_usage',
              'total_vcpus_usage', 
              'total_vcpus','total_memory_mb','total_disk_gb','active_instance' ]

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
        return getattr(self,"active_instance",0)

    @property
    def vcpus(self):
#        return sum(s['vcpus'] for s in self.server_usages
#                   if s['ended_at'] is None)
        return getattr(self,"total_vcpus",0) 

    @property
    def vcpu_hours(self):
        return getattr(self, "total_vcpus_usage", 0)

    @property
    def local_gb(self):
#        return sum(s['local_gb'] for s in self.server_usages
#                   if s['ended_at'] is None)
        return getattr(self,"total_disk_gb",0)

    @property
    def memory_mb(self):
#        return sum(s['memory_mb'] for s in self.server_usages
#                   if s['ended_at'] is None)
        return getattr(self,"total_memory_mb",0)

    @property
    def disk_gb_hours(self):
        return getattr(self, "total_local_gb_usage", 0)

    @property
    def memory_mb_hours(self):
        return getattr(self, "total_memory_mb_usage", 0)


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
    url = 'http://localhost:5001/admin/overview?start=%s&end=%s' % (start.isoformat(),end.isoformat())

    resp_func = requests.request
    resp = resp_func(method,url)
    
    try:
        body = json.loads(resp.text)
    except ValueError:
        body = None
   
    try:
        data = body['projects']
    except KeyError:
        data = None

    _tmp = [SimpleNovaclient(t) for t  in data]
    return [NovaUsage(u) for u in _tmp]

#def usage_get(request, tenant_id, start, end):
#    return NovaUsage(novaclient(request).usage.get(tenant_id, start, end))


#def usage_list(request, start, end):
#    return [NovaUsage(u) for u in
#            novaclient(request).usage.list(start, end, True)]


