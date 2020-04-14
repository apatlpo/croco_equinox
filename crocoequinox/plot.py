import threading

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.geodesic as cgeo
from cmocean import cm

import numpy as np
import pandas as pd

_default_cmaps = {'SSU': cm.balance, 'SSV': cm.balance,
           'SSU_geo': cm.balance, 'SSV_geo': cm.balance,
           'Eta': plt.get_cmap('RdGy_r'),
           'SST': cm.thermal, 'SSS': cm.haline}

def _get_cmap(v, cmap):
    if cmap is None and v.name in _default_cmaps:
        return _default_cmaps[v.name]
    elif cmap is not None:
        return cmap
    else:
        return plt.get_cmap('magma')

#------------------------------ plot ---------------------------------------

#
def plot_scalar(v, colorbar=False, title=None, vmin=None, vmax=None, savefig=None,
                offline=False, coast_resolution='110m', figsize=(10,10), cmap=None):
    #
    if vmin is None:
        vmin = v.min()
    if vmax is None:
        vmax = v.max()
    #
    MPL_LOCK = threading.Lock()
    with MPL_LOCK:
        if offline:
            plt.switch_backend('agg')
        colmap = _get_cmap(v, cmap)
        #
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection=ccrs.PlateCarree())
        try:
            im = v.plot.pcolormesh(ax=ax, transform=ccrs.PlateCarree(), vmin=vmin, vmax=vmax,
                                   x='XC', y='YC', add_colorbar=colorbar, cmap=colmap)
            fig.colorbar(im)
            gl=ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=2, color='k',
                            alpha=0.5, linestyle='--')
            gl.xlabels_top = False
            if coast_resolution is not None:
                ax.coastlines(resolution=coast_resolution, color='k')
        except:
            pass
        #
        if title is not None:
            ax.set_title(title)
        #
        if savefig is not None:
            fig.savefig(savefig, dpi=150)
            plt.close(fig)
        #
        #if not offline:
        #    plt.show()
        return fig, ax

#------------------------------ pretty ---------------------------------------


_region_params = {'atlantic':
                        {'faces':[0,1,2,6,10,11,12],
                        'extent':[-110,25,-70,70],
                        'dticks':[10,10],
                        'projection': ccrs.Mollweide()},
                  'south-atlantic':
                        {'faces':[1,11,0,12],
                        'extent':[-50,20,-60,5],
                        'dticks':[10,10],
                        'projection': ccrs.LambertAzimuthalEqualArea(central_longitude=-15.,
                                                                     central_latitude=-30)}}
#                  'south-atlantic':{'faces':[0,1,11,12],'extent':[-100,25,-70,5]},}

def plot_pretty(v, colorbar=False, title=None, vmin=None, vmax=None, savefig=None,
                offline=False, coast_resolution='110m', figsize=(15,15), cmap=None,
                ignore_face=[], projection=None, extent=None, region=None,
                colorbar_kwargs={}):
    #
    if vmin is None:
        vmin = v.min()
    if vmax is None:
        vmax = v.max()
    #
    MPL_LOCK = threading.Lock()
    with MPL_LOCK:
        if offline:
            plt.switch_backend('agg')
        colmap = _get_cmap(v, cmap)
        #
        if 'face' not in v.dims:
            v = v.expand_dims('face')
        if region is not None:
            if isinstance(region,dict):
                params = region
            else:
                params = _region_params[region]
            _extent = params['extent']
            gen = (face for face in params['faces']
                   if face not in ignore_face)
            _projection = params['projection']
            _dticks = params['dticks']
        else:
            gen = (face for face in v.face.values if face not in ignore_face)
            _projection = ccrs.Robinson()
            _extent = None
        if extent is not None:
            _extent = extent
        if projection is not None:
            _projection = projection
        #
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection=_projection)
        if _extent is not None:
            ax.set_extent(_extent)
        for face in gen:
            vplt = v.sel(face=face)
            if face in [6,7,8,9]:
                # this deals with dateline crossing areas
                im = vplt.where( (vplt.XC>0) & (vplt.XC<179.)).plot.pcolormesh(ax=ax,
                                transform=ccrs.PlateCarree(), vmin=vmin, vmax=vmax,
                                x='XC', y='YC', cmap=colmap, add_colorbar=False)
                im = vplt.where(vplt.XC<0).plot.pcolormesh(ax=ax,
                                transform=ccrs.PlateCarree(), vmin=vmin, vmax=vmax,
                                x='XC', y='YC', cmap=colmap, add_colorbar=False)
            else:
                im = vplt.plot.pcolormesh(ax=ax,
                                transform=ccrs.PlateCarree(), vmin=vmin, vmax=vmax,
                                x='XC', y='YC', cmap=colmap, add_colorbar=False)
        if colorbar:
            cbar = fig.colorbar(im, **colorbar_kwargs)
        else:
            cbar = None
        # grid lines:
        xticks = np.arange(_extent[0],
                           _extent[1]+_dticks[0],
                           _dticks[1]*np.sign(_extent[1]-_extent[0]))
        ax.set_xticks(xticks,crs=ccrs.PlateCarree())
        yticks = np.arange(_extent[2],
                           _extent[3]+_dticks[1],
                           _dticks[1]*np.sign(_extent[3]-_extent[2]))
        ax.set_yticks(yticks,crs=ccrs.PlateCarree())
        #gl = ax.gridlines()
        gl = ax.grid()
        #ax.set_xticks([0, 60, 120, 180, 240, 300, 360], crs=ccrs.PlateCarree())
        #ax.set_yticks([-90, -60, -30, 0, 30, 60, 90], crs=ccrs.PlateCarree())
        #lon_formatter = LongitudeFormatter(zero_direction_label=True)
        #lat_formatter = LatitudeFormatter()
        #ax.xaxis.set_major_formatter(lon_formatter)
        #ax.yaxis.set_major_formatter(lat_formatter)
        # only with platecarre
        #if projection is 'PlateCarre':
        #    gl=ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=2, color='k',
        #                    alpha=0.5, linestyle='--')
        #    gl.xlabels_top = False

        # coastlines and land:
        #if coast_resolution is not None:
        #    ax.coastlines(resolution=coast_resolution, color='k')
        ax.add_feature(cfeature.LAND)
        #
        if title is not None:
            ax.set_title(title,fontdict={'fontsize':20, 'fontweight':'bold'})
        #
        if savefig is not None:
            fig.savefig(savefig, dpi=150)
            plt.close(fig)
        #
        #if not offline:
        #    plt.show()
        return {'fig': fig, 'ax': ax, 'cbar': cbar}

