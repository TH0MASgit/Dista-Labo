from datetime import datetime, timedelta

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.image as mplimg
import matplotlib.animation as mplani

from db.distaDB import *
from heatmap import *


T_hold = 100 #CONSTANTE Le delai entre chaque nouvelle image (en ms)
X_bounds = (30, 60)
Y_bounds = (20, 60)

fig, (left_plt, right_plt) = plt.subplots(1, 2)
fig.autofmt_xdate()


def draw_heatmap(subplot, x_mesh, y_mesh, intensity) :
    bg_img = mplimg.imread(r"db/samples/Carte_5e_etage.png")
    subplot.cla()
    
    subplot.set_title("Heatmap")
    subplot.imshow(bg_img, extent=[*X_bounds, *Y_bounds])
    subplot.contourf(x_mesh, y_mesh, intensity, levels=[-2, -1, 0, 1, 2], extend='both',
                     colors=['red', 'white', 'green', 'yellowgreen'], alpha=0.4)

# Some settings that work well:
# Detection density: levels=[-1, -0.5, 0, 0.5, 1], colors=['red', 'white', 'green', 'orange']
# Collision density: levels=[-2, -1.5, -1, -0.5, 0], colors=['red', 'orange', 'green', 'white']
# Collision highlights: levels=[-2, -1, 0, 1, 2], colors=['red', 'white', 'green', 'yellowgreen']
#                                              or colors=['red', 'white', 'blue', 'darkviolet']


def draw_chart(subplot, x_time, y_personnes, y_collisions) :
    subplot.cla()
    subplot.set_title("Nombre de personnes/collisions")
    subplot.set_ylim(0, max(max(y_personnes), 10))
    
    n_personnes = y_personnes[-1]
    n_collisions = y_collisions[-1]
    subplot.annotate('%.1f' % n_personnes, xy=(x_time[-1], n_personnes))
    subplot.annotate('%.1f' % n_collisions, xy=(x_time[-1], n_collisions))
    
    #subplot.set_xlabel('Temps')
    subplot.plot(x_time, y_personnes, 'blue', label="Nombre de personnes")
    subplot.plot(x_time, y_collisions, 'red', label="Nombre de collisions")
    subplot.legend()


def animate_frame(ts, db, step, L_timestamps, N_personnes, N_collisions) :
    print('t =', ts.strftime('%Y-%m-%d %H:%M:%S'))
    sampling_interval = max(step.total_seconds() / 10, 1)
    df,nb_samples = get_historical_data(db, ts, ts + step, sampling_interval)
    
    x_data = (df['X']/100).to_numpy()
    y_data = (df['Y']/100).to_numpy()
    
    draw_heatmap(left_plt, *compute_heatmap(x_data, y_data, *X_bounds, *Y_bounds))
    left_plt.plot(x_data, y_data, 'b.')
    
    if nb_samples > 0 :
        N_personnes.append(len(df) / nb_samples)
        N_collisions.append(len(df[df['D_min'] < D_critique]) / nb_samples)
    else :
        N_personnes.append(0)
        N_collisions.append(0)
    
    L_timestamps.append(ts)
    if len(L_timestamps) > 5 :
        L_timestamps.pop(0)
        N_personnes.pop(0)
        N_collisions.pop(0)
    
    draw_chart(right_plt, L_timestamps, N_personnes, N_collisions)
    fig.autofmt_xdate()


def animate_realtime(db, start_time=None) :
    offset = datetime.now() - start_time if start_time else timedelta(milliseconds=T_hold)
    def gen_ts() :
        while True :
            yield datetime.now() - offset
    
    return mplani.FuncAnimation(fig, animate_frame, fargs=(db, timedelta(0), [], [], []),
                                frames=gen_ts, interval=T_hold, repeat=False, save_count=50)


def animate_historical(db, start_time, duration=timedelta(hours=1), step=timedelta(minutes=1)) :
    L_frames = [start_time + timedelta(seconds=ds)
                for ds in range(0, int(duration.total_seconds()), int(step.total_seconds()))]
    
    return mplani.FuncAnimation(fig, animate_frame, fargs=(db, step, [], [], []),
                                frames=L_frames, interval=T_hold, repeat=False, save_count=50)


if __name__ == '__main__' : # Lancez-moi avec `cd .. ; python -m viz.realtime_charts
    #db = DistaDB(r"db/samples/dista_ete_06-29_au_07-02_globale.sqlite")
    db = DistaDB("mariadb:dista.cuyasziqzqwn.us-east-1.rds.amazonaws.com/dista-test")
    dt = datetime(2020,7,2,8,30,0)
    
    ani = animate_realtime(db, start_time=dt+timedelta(minutes=50))
    #ani = animate_historical(db, start_time=dt, duration=timedelta(hours=4), step=timedelta(minutes=5))
    
    save = False
    if save :
        slow_down = 0.5 # we need to slow down the saved animation so it matches the live version
        gif_path = r"viz/samples/animation.gif"
        gif_writer = mplani.PillowWriter(fps=slow_down*1000/T_hold)
        ani.save(gif_path, writer=gif_writer)
        print("Saved to", gif_path)
    else :
        plt.show()
