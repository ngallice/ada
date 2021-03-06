import pandas as pd
import numpy as np

import pickle

import os

from bokeh.io import output_file, show, export_svgs
from bokeh.layouts import widgetbox, row, column
from bokeh.models.widgets import Select, CheckboxGroup
from bokeh.models.widgets import RangeSlider, Slider
from bokeh.models import ColumnDataSource, HoverTool, Div, Range1d
from bokeh.plotting import curdoc, figure
from bokeh.client import push_session
from bokeh.layouts import layout, widgetbox
from bokeh.charts import Donut


f = open('dataframe-final', 'rb')
df = pickle.load(f)

genre_color={'blues':'#75bbfd','country':'#653700','electronica':'#9a0eea','folk':'#f97306','jazz':'#fac205',
             'pop':'#ff81c0','metal':'#000000','rock':'#2242c7','orchestral':'#929591','hiphop':'#e50000',
             'reggae':'#02ab2e','world':'#a0bf16','all':'#0485d1'}

genre_idx={'blues':6,'country':5,'electronica':11,'folk':4,'jazz':8,
             'pop':10,'metal':7,'rock':12,'orchestral':1,'hiphop':9,
             'reggae':2,'world':3}

df['color']=df.genre.apply(lambda genre: genre_color[genre])
df['gid']=df.genre.apply(lambda genre: genre_idx[genre])

genre_list = ['all']

for g in df['genre'].unique():
    genre_list.append(g)


columns =['song_hotttnesss','year','duration','loudness','tempo','artist_hotttnesss','artist_familiarity','gid']


def song_selected():
    (start, end) = year_slider.value


    selected = df[(df.year >= start) & (df.year <= end)]


    selected=selected.sort_values(['song_hotttnesss'], ascending=[0])


    selected=selected.head(var_slider.value)

    return selected


def distribution():
    (start, end) = year_slider.value


    selected = df[(df.year >= start) & (df.year <= end) & (df.song_hotttnesss>0)]
    selected=selected.sort_values(['song_hotttnesss'], ascending=[0])

    col=dico_fig2[fig2.value]

    if col != 'loudness':
        selected=selected[selected[col]!=0]

    if col=='duration':
        selected = selected[selected[col] <700]



    selected=selected[col]
    return selected



def update(attr, old, new):
    p, q = create_figure()
    layout.children[1] = p
    layout.children[2] = q

#columns =['song_hotttnesss','year','duration','loudness','tempo','artist_hotttnesss','artist_familiarity']


x = Select(title='X-Axis', value='gid', options=columns)
x.on_change('value', update)

y = Select(title='Y-Axis', value='song_hotttnesss', options=columns)
y.on_change('value', update)

var_slider = Slider(start=100, end=2000, value=1000, step=100, title="The # most hottt songs")
var_slider.on_change('value', update)

#checkbox_year = CheckboxGroup(labels=["Show songs with missing year"], active=[])
#checkbox_year.on_change('active', update)

year_slider = RangeSlider(start=1940, end=2011, value=(1940,2011), step=5, title="year")
year_slider.on_change('value', update)

dico_fig2={'year distribution':'year','duration distribution':'duration','loudness distribution':'loudness','tempo distribution':'tempo',
           'artist hotttnesss distribution':'artist_hotttnesss','artist familiarity distribution':'artist_familiarity','genre distribution':'genre'}

fig2 = Select(title='Right figure', value='genre pie chart', options=['genre pie chart','year distribution','duration distribution','loudness distribution','tempo distribution',
           'artist hotttnesss distribution','artist familiarity distribution','genre distribution'])
fig2.on_change('value', update)


def create_figure():
    q = figure(plot_height=400, plot_width=400, tools=[])

    data = song_selected()

    p = figure(plot_height=400, plot_width=400)
    if len(data) > 0:
        hover = HoverTool(tooltips=[
            ("Artist", "@artist"),
            ("Title","@title"),
            ("Year", "@year"),
            ("Genre", "@genre")

        ])

        source = ColumnDataSource(data=dict(artist=data.artist_name,title=data.title, genre=data.genre, year=data.year))

        xs = data[x.value].values
        ys = data[y.value].values
        x_title = x.value.title()
        y_title = y.value.title()

        title = 'The {} hotttest songs'.format( var_slider.value)
        p = figure(plot_height=400, plot_width=400, title=title, tools=[hover, 'box_zoom', 'wheel_zoom','pan'])

        p.circle(x=xs, y=ys, source=source, color=data.color, line_color="White", alpha=0.6,
                 hover_color='white', hover_alpha=0.5)

        #p.xaxis.axis_label = x_title
        p.xaxis.visible = False
        p.yaxis.axis_label = y_title

        count = data.genre.value_counts()

        colors = [genre_color[x] for x in count.index.sort_values()]


        if fig2.value == "genre pie chart":
            q = Donut(count, label='index', color=colors, height=400, width=400,hover_text='#songs')
            q.title.text = '{} hotttest songs'.format( var_slider.value)

            (start, end) = year_slider.value

            data2 = df[(df.year >= start) & (df.year <= end)]
            count2 =  data2.genre.value_counts()

            r = Donut(count2, label='index', color=colors, height=400, width=400, hover_text='#songs')
            r.title.text ="all songs"


        else:

            col=dico_fig2[fig2.value]
            q = figure(plot_height=400, plot_width=400,title=fig2.value, tools="save")

            hist, edges = np.histogram(data[col], density=True, bins=50)

            q.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
                fill_color="#cb416b", line_color="#033649",alpha=0.5,legend='{} hotttest songs'.format( var_slider.value))

            q.xaxis.axis_label = col


            hist2, edges2 = np.histogram(distribution(), density=True, bins=50)

            q.quad(top=hist2, bottom=0, left=edges2[:-1], right=edges2[1:],
                  fill_color="#75bbfd", line_color="#033649",alpha=0.5,legend="all songs")

            if col == 'duration':
                q.x_range = Range1d(0, 700)
                q.legend.location= "top_right"

            elif col== 'tempo':
                q.legend.location = "top_right"
            else:
                q.legend.location = "top_left"

    return p, q,r


controls = widgetbox([var_slider,x,y,year_slider,fig2], width=200)

# layout =row(controls, create_figure())
a, b,c = create_figure()
layout = row(controls, a, b)

curdoc().add_root(layout)
curdoc().title = "Hottness_familiarity"
plots = {'1': a, '2': b,'3':c}

from bokeh.embed import components
script, div = components(plots)
print(script)
print(div)