import os
from glob import glob
import numpy as np
import xarray as xr
from pandas import DataFrame, Series

import datetime, dateutil

#------------------------------ parameters -------------------------------------

g = 9.81
omega_earth = 2.*np.pi/86164.0905
deg2rad = np.pi/180.
deg2m = 111319

#------------------------------ paths ---------------------------------------

if os.path.isdir('/home/datawork-lops-osi/'):
    # datarmor
    plateform='datarmor'
    datawork = os.getenv('DATAWORK')+'/'
    home = os.getenv('HOME')+'/'
    scratch = os.getenv('SCRATCH')+'/'
    osi = '/home/datawork-lops-osi/'
    #
    root_data_dir = '/home/datawork-lops-osi/equinox/mit4320/'
    #
    bin_data_dir = root_data_dir+'bin/'
    bin_grid_dir = bin_data_dir+'grid/'
    #
    zarr_data_dir = root_data_dir+'zarr/'
    zarr_grid = zarr_data_dir+'grid.zarr'
    mask_path = zarr_data_dir+'mask.zarr'
elif os.path.isdir('/work/ALT/swot/'):
    # hal
    plateform='hal'
    tmp = os.getenv('TMPDIR')
    home = os.getenv('HOME')+'/'
    scratch = os.getenv('HOME')+'/scratch/'
    #
    root_data_dir = '/work/ALT/swot/swotpub/LLC4320/'
    work_data_dir = '/work/ALT/swot/aval/syn/'
    #grid_dir = root_data_dir+'grid/'
    #grid_dir_nc = root_data_dir+'grid_nc/'
    enatl60_data_dir = '/work/ALT/odatis/eNATL60/'


#------------------------------ misc ---------------------------------------
                        
def getsize(dir_path):
    ''' Returns the size of a directory in bytes
    '''
    process = os.popen('du -s '+dir_path)
    size = int(process.read().split()[0]) # du returns kb
    process.close()
    return size*1e3

