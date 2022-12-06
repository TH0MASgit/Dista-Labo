import math
from datetime import datetime, timedelta

import pandas as pd
import numpy as np
from scipy.spatial.distance import pdist, squareform

from db.distaDB import *

Camera = 2 #FIXME Devrait etre un parametre!

Grid_size = 0.15 #CONSTANTE La taille des tuiles (~15 cm)
D_critique = 200 #CONSTANTE La distance de collision (2m)

# for benchmarking only
from time import time
duration_ms = 0


def compute_min_dist(sample_df) : #TODO move me to realtime_charts (or add me to SQL)
    dist_mat = squareform(pdist(sample_df[['X', 'Y']].to_numpy()))
    np.fill_diagonal(dist_mat, np.inf)
    min_dist = np.min(dist_mat, axis=1)
    sample_df['D_min'] = min_dist
    return sample_df

def get_historical_data(db, start_dt, end_dt, sample_interval) :
    df = db.select_sampled_positions(Camera, start_dt, end_dt, sample_interval) #FIXME handle all cameras
    df.dropna(inplace=True)
    df['D_min'] = df.groupby('time').apply(compute_min_dist)['D_min'] if not df.empty else None
    
    nb_samples = df['time'].nunique()
    return df, nb_samples

def get_realtime_data(db, dt) :
    #return get_historical_data(db, dt, dt, 1) This also works, but it's slower
    df = db.select_sampled_positions(camera=1, start_time=dt, end_time=dt)
    df.dropna(inplace=True)
    df['D_min'] = compute_min_dist(df)['D_min'] if not df.empty else None
    return df, 1


class KDE :
    H = D_critique/100
    HH = H/2

    @staticmethod
    def quartic(d) :
        if d > KDE.H :
            return (0, 0)
        dn = d/KDE.H
        P = (15/16) * (1 - dn**2)**2
        return (P, 1 if d < KDE.HH else 0)
    
    @staticmethod
    def discrete(d) :
        if d > KDE.H :
            return (0, 0)
        return (1, 1 if d < KDE.HH else 0)


def compute_heatmap(x, y, x_min, x_max, y_min, y_max, kde_func=KDE.quartic) :
    global duration_ms
    t0 = time()
    
    def real_to_grid(px, py) :
        # Yes, the coordinates must be transposed
        return (int((py - y_min) / Grid_size), int((px - x_min) / Grid_size))
    
    x_grid = np.arange(x_min, x_max, step=Grid_size)
    y_grid = np.arange(y_min, y_max, step=Grid_size)
    x_mesh,y_mesh = np.meshgrid(x_grid, y_grid)
    
    intensity = np.zeros_like(x_mesh, dtype=np.double) # x_mesh.shape == y_mesh.shape
    collision = np.ones_like(intensity, dtype=np.byte)
    
    B = int(KDE.H/Grid_size) + 1 #TODO technically we want ceil_away_from_0 here
    for px,py in zip(x, y) :
        gx,gy = real_to_grid(px, py)
        x_slice = slice(max(gx - B, 0), min(gx + B + 1, intensity.shape[0]))
        y_slice = slice(max(gy - B, 0), min(gy + B + 1, intensity.shape[1]))
        
        x_center = x_mesh[x_slice, y_slice] + Grid_size/2
        y_center = y_mesh[x_slice, y_slice] + Grid_size/2
        
        slice_z = intensity[x_slice, y_slice]
        slice_c = collision[x_slice, y_slice]
        
        # slice_z += 1
        # slice_v *= 2
        for i in range(slice_z.shape[0]) :
            for j in range(slice_z.shape[1]) :
                d = math.sqrt((x_center[i,j] - px)**2 + (y_center[i,j] - py)**2)
                z,c = kde_func(d)
                slice_z[i, j] += z
                slice_c[i, j] -= c
    
    # Make all cells where collisions occured negative:
    intensity *= (collision >> 7) * 2 + 1 # right shift is arithmetic in python/numpy
    
    duration_ms = 0.9*duration_ms + 0.1*1000*(time() - t0)
    print("duration =", int(duration_ms), "ms")
    return (x_mesh, y_mesh, intensity)


def get_heatmap_plotly(db, dt=datetime.now(), x_min=0, x_max=20, y_min=0, y_max=25) :
    (df, nb_samples) = get_realtime_data(db, dt)
    x_data = (df['X']/100 - 35).to_numpy() #TODO normalize center position automatically
    y_data = (df['Y']/100 - 28).to_numpy() # (either with mean on (x,y) or camera position)
    
    (x_mesh, y_mesh, intensity) = compute_heatmap(x_data, y_data, x_min, x_max, y_min, y_max)
    return (x_mesh[0, :], y_mesh[:, 0], intensity)


def get_heatmap_heatmapjs(db, dt=datetime.now(), x_min=0, x_max=20, y_min=0, y_max=25) :
    (df, nb_samples) = get_realtime_data(db, dt)
    x_data = (df['X']/100 - 35).to_numpy() #TODO normalize center position automatically
    y_data = (df['Y']/100 - 28).to_numpy() # (either with mean on (x,y) or camera position)
    
    (x_mesh, y_mesh, intensity) = compute_heatmap(x_data, y_data, x_min, x_max, y_min, y_max)
    data = np.dstack((x_mesh, y_mesh, intensity))
    return data.reshape(data.shape[0] * data.shape[1], 3)


def start_stream(db, start_time=datetime.now(), format='plotly', x_min=0, x_max=20, y_min=0, y_max=25) :
    import time
    interval = timedelta(seconds=1)
    
    dt = start_time
    while True :
        (x_ticks, y_ticks, z_mat) = get_heatmap_plotly(db, dt)
        #print([x_ticks, y_ticks, z_mat.tolist()])
        dt += interval
        time.sleep(1)


if __name__ == '__main__' :
    db = DistaDB('db/samples/dista_ete_06-29_au_07-02_globale.sqlite')
    dt = datetime(2020,7,2,8,30,0)
    
    # (df, nb_samples) = get_realtime_data(db, dt)
    # # (df, nb_samples) = get_historical_data(db, dt, dt+timedelta(seconds=600), 60)
    # print(f"db returned {nb_samples} samples for t = {dt}")
    # x_data = (df['X']/100 - 35).to_numpy() #TODO normalize center position automatically
    # y_data = (df['Y']/100 - 28).to_numpy() # (either with mean on (x,y) or camera position)
    
    # (x_mesh, y_mesh, intensity) = compute_heatmap(x_data,y_data, 0,20, 0,25)
    # condensed = intensity[~np.all(intensity == 0, axis=1)]
    # condensed = condensed[:, ~np.all(condensed == 0, axis=0)]
    # print(f"condensed heatmap data {condensed.shape} :\n{condensed}")
    # print(f"full size was {intensity.shape}")
    
    # data_points = get_heatmap_heatmapjs(db, dt)
    # print(data_points.shape)
    # print(data_points.tolist())
    
    # (x_ticks, y_ticks, z_mat) = get_heatmap_plotly(db, dt)
    # print(x_ticks)
    # print(y_labels)
    # condensed = z_mat[~np.all(z_mat == 0, axis=1)]
    # condensed = condensed[:, ~np.all(condensed == 0, axis=0)]
    # print(f"condensed heatmap data {condensed.shape} :\n{condensed}")
    # print(f"full size was {z_mat.shape}")

    # #print(np.all(intensity == z_mat))
    
    # import plotly.express as px
    # fig = px.imshow(z_mat,
                    # labels=dict(x="x", y="y", color="Intensity"),
                    # x=x_ticks, y=y_labels
                   # )
    # fig.update_xaxes(side="top")
    # fig.show()
    
    start_stream(db, dt)
    