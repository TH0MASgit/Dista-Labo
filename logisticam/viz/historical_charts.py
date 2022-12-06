import pandas as pd

# We use Plotly to generate the graphs: https://plotly.com/python/
import plotly.express as px
import plotly.graph_objects as go

from db.distaDB import DistaDB


def add_gaps(df, time_delta) :
    gaps_buffer = []
    
    for cam in df['camera'].unique() :
        single_cam = df.loc[df['camera'] == cam]
        time_gaps = single_cam.loc[single_cam['time'].diff() > time_delta].copy()
        time_gaps.index -= 0.5
        time_gaps['time'] -= time_delta
        time_gaps['data'] = None
        gaps_buffer.append(time_gaps)
    
    df = df.append(gaps_buffer, ignore_index=False)
    return df.sort_index()#.reset_index(drop=True)


def prepare_data(queries, timeslice) :
    if not hasattr(queries, "__iter__") :
        queries = [queries]
    
    # Fetching data
    data_frames = [query(time_interval=timeslice) for query in queries]
    data_labels = [(query.__name__.split('_', 1))[-1] for query in queries]
    
    # Reordering columns
    # cols = list(data_frames[0])
    # cols.remove(data_labels[0])
    # cols.append(data_labels[0])
    # data_frames[0] = data_frames[0][cols]
    
    # Renaming data columns
    for df, dl in zip(data_frames, data_labels) :
        df.rename(columns={dl: 'data'}, inplace=True)
    
    # Adding time "gaps" (to split the lines on missing data)
    data_frames = [add_gaps(df, pd.Timedelta(timeslice, 's')) for df in data_frames]
    
    # Concatenating all data
    return pd.concat(data_frames, keys=data_labels, names=['query', 'idx'])


def generate_single_graph(df, title="", ylabel="") :
    # Ref: https://plotly.com/python/line-charts/

    # With Plotly Express:
    fig = px.line(df, x='time', y='data', color='camera', title=title,
                  labels={'time':"temps", 'data':ylabel, 'camera':"caméra"})
    
    fig.update_yaxes(rangemode = 'tozero')
    
    # Configureing the graph 'extras' (like the slider below)
    fig.update_xaxes(matches='x')
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=15, label="15m", step='minute', stepmode='backward'),
                dict(count=3, label="3h", step='hour', stepmode='backward'),
                dict(count=1, label="1d", step='day', stepmode='backward'),
                dict(step='all')
            ])
        )
    )
    
    return fig


def generate_multi_graph(df, title="", ylabels=[]) :
    # Preparing graph
    fig = px.line(df, x='time', y='data', color='camera', title=title,
                  labels={'time':"temps", 'data':"", 'camera':"caméra"},
                  facet_row=df.index.get_level_values('query'))
    
    # Customizing graph look
    fig.update_yaxes(rangemode = 'tozero')
    
    if ylabels :
        ylabels.reverse() # yaxis title order is inverted in plotly
    else :
        fig.for_each_annotation(lambda a: ylabels.append(a.text.split('=')[-1]))
    
    fig.layout.annotations = ()
    for i in range(len(ylabels)) :
        fig['layout']['yaxis' + str(i + 1)]['title'] = ylabels[i]
    
    fig.update_yaxes(matches=None) # Allow graphs to have different axis ranges
    return fig


if __name__ == "__main__" : # Call me using `cd logisticam; python -m viz.historical_charts`
    db = DistaDB("db/samples/dista_ete_06-29_au_07-02_globale.sqlite")
    #db = DistaDB("mysql:192.168.0.19/dista_test6")
    #db = DistaDB("mysql:10.180.5.121/dista")
    
    queries = [db.select_nb_detections, db.select_nb_colliding_detections,
               db.select_nb_collisions, db.select_avg_closest_neighbor]
    
    # Generating a single graph ================================================
    # df = prepare_data(queries[0], 300)
    # print(df)
    
    # fig = generate_single_graph(df,
        # "Nombre de personnes détectées en fonction du temps",
        # "nb. de détections")
    # fig.show()
    
    # Generating a multi-graph =================================================
    df = prepare_data(queries, 300)
    
    # Custom data post-processing to display percent of people colliding
    df.loc[('nb_colliding_detections', slice(None)), 'data'] /= df.loc['nb_detections', 'data']
    df.rename(index={'nb_colliding_detections':'pct_colliding_detections'}, inplace=True)
    df.drop(index='nb_detections', inplace=True)
    print(df)
    
    # Display distances in m (instead of cm)
    df.loc[('avg_closest_neighbor', slice(None)), 'data'] /= 100
    print(df.loc['avg_closest_neighbor'])
    
    fig = generate_multi_graph(df,
        "Résultats du projet pilote Dista-CAL (été 2020)",
        ["% des détections<br>en état de collision",
         "nb. de collisions<br>(interactions <2m)",
         "distance au plus<br>proche voisin (m)"])
    
    # Custom graph formatting
    fig.layout.yaxis3.tickformat = '.0%'
    fig.layout.yaxis3.range = [0, 1]
    # fig.update_yaxes(matches='y3')
    # fig.layout.yaxis.matches = None
    
    fig.show()
    
    # Graphic for the report ===================================================
    # queries = [db.select_nb_detections, db.select_nb_collisions]
    # df = prepare_data(queries, 180)
    
    # # Custom data post-processing
    # print(df)
    
    # fig = generate_multi_graph(df,
        # "Résultats du projet pilote Dista-CAL (été 2020)",
        # ["nb. de personnes", "nb. d'interactions <2m"])
    
    # fig.show()
    