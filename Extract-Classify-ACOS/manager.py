# -*- coding: utf-8 -*-
"""
Created on Mon Aug  7 19:38:30 2017

@author: Quantum Liu
"""

'''
Example:
gm=GPUManager()
with gm.auto_choice():
    blabla
'''

import os
import pdb
import sched, time
import datetime
#from tensorflow.python.client import device_lib

def check_gpus():
    '''
    GPU available check
    '''
    try:
        lines = os.popen('nvidia-smi --query-gpu=index --format=csv,noheader').readlines()
        if len(lines) == 0:
            return False
        return True
    except Exception:
        return False

def parse(line,qargs):
    numberic_args = ['memory.free', 'memory.total', 'power.draw', 'power.limit']
    power_manage_enable=lambda v:(not 'Not Support' in v)
    to_numberic=lambda v:float(v.upper().strip().replace('MIB','').replace('W',''))
    process = lambda k,v:((int(to_numberic(v)) if power_manage_enable(v) else 1) if k in numberic_args else v.strip())
    return {k:process(k,v) for k,v in zip(qargs,line.strip().split(','))}

def query_gpu(qargs=[]):
    qargs =['index','gpu_name', 'memory.free', 'memory.total', 'power.draw', 'power.limit', 'utilization.gpu']+ qargs
    try:
        cmd = 'nvidia-smi --query-gpu={} --format=csv,noheader'.format(','.join(qargs))
        results = os.popen(cmd).readlines()
        if not results:
            return [{'index': '0', 'gpu_name': 'GPU-0', 'memory.free': 10000, 'memory.total': 10000, 'power.draw': 0, 'power.limit': 100, 'utilization.gpu': 0}]
        return [parse(line,qargs) for line in results]
    except Exception:
        return [{'index': '0', 'gpu_name': 'GPU-0', 'memory.free': 10000, 'memory.total': 10000, 'power.draw': 0, 'power.limit': 100, 'utilization.gpu': 0}]

def by_power(d):
    power_infos=(d.get('power.draw', 0), d.get('power.limit', 100))
    if any(v==1 for v in power_infos):
        return 1
    return float(d.get('power.draw', 0))/max(float(d.get('power.limit', 100)), 1.0)

class GPUManager():
    def __init__(self,qargs=[]):
        self.qargs=qargs
        try:
            self.gpus=query_gpu(qargs)
        except Exception:
            self.gpus=[{'index': '0', 'gpu_name': 'GPU-0', 'memory.free': 10000, 'memory.total': 10000, 'power.draw': 0, 'power.limit': 100, 'utilization.gpu': 0}]
        for gpu in self.gpus:
            gpu['specified']=False
        self.gpu_num=len(self.gpus)

    def _sort_by_memory(self,gpus,by_size=False):
        if by_size:
            return sorted(gpus,key=lambda d:d.get('memory.free', 0),reverse=True)
        else:
            return sorted(gpus,key=lambda d:float(d.get('memory.free', 0))/ max(float(d.get('memory.total', 1)), 1.0),reverse=True)

    def _sort_by_power(self,gpus):
        return sorted(gpus,key=by_power)

    def auto_choice(self,mode=0):
        if not self.gpus:
            return "0"
        try:
            chosen_gpu = self._sort_by_memory(self.gpus, True)[0]
            chosen_gpu['specified'] = True
            index = chosen_gpu['index']
            print(f"Using GPU {index}")
            return str(index)
        except Exception:
            return "0"
# else:
#     raise ImportError('GPU available check failed')
