from typing import List, Union


def nwp_gribfiles_avalibel_steps(logger, parm, datum, avalible_steps):
    '''Eine Funktion zum durchsuchen der zur Verfügung stehenden NWP Forcasts
    path_nwp_forcasts = str
    '''
    import os
    path_nwp_forcasts = './data/grib/gfs_forcast/{}/{}0000/'.format(parm, datum)

    def mainfunktion(path_nwp_forcast, avg_spr):
        nwp_gribfiles_avalible_steps: List[Union[bytes, str]] = []
        for dirpath, subdirs, files in os.walk(path_nwp_forcasts):
            for file in files:
                for step in avalible_steps:
                    if avg_spr == "mean":
                        searchstring = "_avg_f{:03d}".format(step)
                    elif avg_spr == "spread":
                        searchstring = "_spr_f{:03d}".format(step)

                    if searchstring in file:
                        nwp_gribfiles_avalible_steps.append(os.path.join(dirpath, file))
                    else:
                        continue

        if nwp_gribfiles_avalible_steps == []:
            logger.error('parm: {:8} | Verfuegabe Files: {} | {} | {}'.format(parm, len(nwp_gribfiles_avalible_steps), avg_spr, path_nwp_forcasts))
        else:
            logger.info('parm: {:8} | Verfuegabe Files: {} | {} | {}'.format(parm, len(nwp_gribfiles_avalible_steps), avg_spr, path_nwp_forcasts))

        return (sorted(nwp_gribfiles_avalible_steps))
    return mainfunktion(path_nwp_forcasts, 'mean'), mainfunktion(path_nwp_forcasts, 'spread')


def pygribOpen(file):
    import pygrib
    file = pygrib.open(file)
    file = file.select()[0]
    analDate = file.analDate.strftime("%Y-%m-%d %H:%M")
    validDate = file.validDate.strftime("%Y-%m-%d %H:%M")

    return file, analDate, validDate


def plot_forcast(name_parm, m, xx, yy, plotparameter, analDate, validDate, grb_analDate, step, what):
    '''Plotfunktion für Forcast Grafiken
        m = Object vom type BASEMAP
        xx, yy = BASEMAP.meshgrid
        plotparameter = numpy.ndarray
        analDate, validDate, analDate_save_format, = string
        step = integer
        what, parm = string
    '''
    import io
    import os
    import matplotlib.pyplot as plt
    import numpy as np
    #f = io.BytesIO()
    fig = plt.figure(figsize=(15, 15), dpi=96)
    #Plot Eigenschaften
    #SAMOS t
    if name_parm == 'tmp_2m' and what == 'samos_mean':
        m.pcolormesh(xx, yy, plotparameter, shading='flat', latlon=True, cmap='RdBu_r')
        plt.title("2m Temperatur SAMOS MEAN [°C]", loc='center')
        plt.clim(-40, 40)
    elif name_parm == 'tmp_2m' and what == 'samos_spread':
        m.pcolormesh(xx, yy, plotparameter, shading='flat', latlon=True, cmap='Reds')
        plt.title("2m Temperatur SAMOS SPREAD [°C]", loc='center')
        plt.clim(0, 5)
    elif name_parm == 'tmp_2m' and what == 'nwp_mean':
        m.pcolormesh(xx, yy, plotparameter, shading='flat', latlon=True, cmap='RdBu_r')
        plt.title("2m Temperatur GFS MEAN [°C]", loc='center')
        plt.clim(-40, 40)
    elif name_parm == 'tmp_2m' and what == 'nwp_spread':
        m.pcolormesh(xx, yy, plotparameter, shading='flat', latlon=True, cmap='Reds')
        plt.title("2m Temperatur GFS SPREAD [°C]", loc='center')
        plt.clim(0, 5)
    elif name_parm == 'rh_2m' and what == 'samos_mean':
        m.pcolormesh(xx, yy, plotparameter, shading='flat', latlon=True, cmap='YlGn')
        plt.title("2m Relative Luftfeuchte SAMOS MEAN [%]", loc='center')
        plt.clim(0, 100)
    elif name_parm == 'rh_2m' and what == 'samos_spread':
        m.pcolormesh(xx, yy, plotparameter, shading='flat', latlon=True, cmap='Reds')
        plt.title("2m Relative Luftfeuchte SAMOS SPREAD [%]", loc='center')
        plt.clim(0, 5)
    elif name_parm == 'rh_2m' and what == 'nwp_mean':
        m.pcolormesh(xx, yy, plotparameter, shading='flat', latlon=True, cmap='YlGn')
        plt.title("2m Relative Luftfeuchte GFS MEAN [%]", loc='center')
        plt.clim(0, 100)
    elif name_parm == 'rh_2m' and what == 'nwp_spread':
        m.pcolormesh(xx, yy, plotparameter, shading='flat', latlon=True, cmap='Reds')
        plt.title("2m Relative Luftfeuchte GFS SPREAD [%]", loc='center')
        plt.clim(0, 5)
    elif name_parm == 'wind_10m' and what == 'samos_mean':
        m.pcolormesh(xx, yy, plotparameter, shading='flat', latlon=True, cmap='Purples')
        plt.title("10m Windgeschwindigkeit SAMOS MEAN [km/h]", loc='center')
        plt.clim(0, 10)
    elif name_parm == 'wind_10m' and what == 'samos_spread':
        m.pcolormesh(xx, yy, plotparameter, shading='flat', latlon=True, cmap='Reds')
        plt.title("10m Windgeschwindigkeit SAMOS SPREAD [km/h]", loc='center')
        plt.clim(0, 10)
    elif name_parm == 'wind_10m' and what == 'nwp_mean':
        m.pcolormesh(xx, yy, plotparameter, shading='flat', latlon=True, cmap='Purples')
        plt.title("10m Windgeschwindigkeit GFS MEAN [km/h]", loc='center')
        plt.clim(0, 10)
    elif name_parm == 'wind_10m' and what == 'nwp_spread':
        m.pcolormesh(xx, yy, plotparameter, shading='flat', latlon=True, cmap='Reds')
        plt.title("10m Windgeschwindigkeit GFS SPREAD [km/h]", loc='center')
        plt.clim(0, 10)


    plt.title("Gültig für {} | Step +{}".format(validDate, step), loc='left')
    plt.title("GFS Lauf {}".format(analDate), loc='right')
    m.colorbar(location='right')
    m.readshapefile("./data/DGM/gadm36_AUT_shp/gadm36_AUT_0", "aut")

    parallels = np.arange(44.5, 52.5, 1.)
    m.drawparallels(parallels, labels=[False, False, False, False], fontsize=8, color='lightgrey')
    meridians = np.arange(8.5, 19.5, 1.)
    m.drawmeridians(meridians, labels=[False, False, False, False], fontsize=8, color='lightgrey')

    parallels = np.arange(45., 53., 1.)
    m.drawparallels(parallels, labels=[True, False, False, False], fontsize=8, linewidth=0.0)
    meridians = np.arange(8., 20., 1.)
    m.drawmeridians(meridians, labels=[False, False, False, True], fontsize=8, linewidth=0.0)

    filepath = './spool/{}/{}/'.format(name_parm, what)
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    figname = '{}_step_{:03d}.png'.format(grb_analDate.strftime("%Y%m%d%H%M"), step)
    file = os.path.join(filepath, figname)
    fig.savefig(file, bbox_inches='tight')
    #plt.savefig(f, bbox_inches='tight')
    plt.close(fig=None)
    return(figname)#, f)


def reshapearea(column, alt):
    '''Eine Funktion zum reshapen von Pandas Dataframe Clumns
    column = pd.Dataframe.Column
    alt = np.ndarray'''
    data = column.values
    reshapedarea = data.reshape(alt.shape)
    reshapedarea = reshapedarea[::-1]
    return (reshapedarea)


#=================
def avaliblelSteps(logger, parm, datum, avalible_steps):
    import sys
    import os
    # Lokale Files
    sys.path.insert(0, os.getcwd())

    path_nwp_forcasts = './data/grib/gfs_forcast/{}/{}0000/'.format(parm, datum)
    nwp_gribfiles_avalibel_mean_steps = nwp_gribfiles_avalibel_steps(path_nwp_forcasts, 'mean', avalible_steps)
    nwp_gribfiles_avalibel_spread_steps = nwp_gribfiles_avalibel_steps(path_nwp_forcasts, 'spread', avalible_steps)

    if nwp_gribfiles_avalibel_mean_steps is []:
        logger.error('Es sind keine Vorhersagen für das eingegebene Datum vorhanden | --datum {} | {}'.format(datum, path_nwp_forcasts))
    else:
        pass

    if nwp_gribfiles_avalibel_spread_steps is []:
        logger.error('Es sind keine Vorhersagen für das eingegebene Datum vorhanden | --datum {} | {}'.format(datum, path_nwp_forcasts))
    else:
        pass

    return nwp_gribfiles_avalibel_mean_steps, nwp_gribfiles_avalibel_spread_steps