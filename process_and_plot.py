import pandas as pd
import numpy as np
import datetime
from bokeh.plotting import figure, output_file, show, ColumnDataSource
from bokeh.transform import factor_cmap
from bokeh.palettes import Spectral6
from bokeh.models import Legend
from bokeh.models import DatetimeTickFormatter
from bokeh.models.widgets import RadioGroup
from bokeh.models.widgets import Panel, Tabs
from collections import Counter
from bokeh.palettes import brewer
from bokeh.palettes import Category20

from bokeh.io import show
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, RangeTool, HoverTool, LabelSet, Span
from bokeh.plotting import figure


def parse_datetime(datetime_strings):

    # take a numpy vector of datetime strings
    # a numpy vector of datetime objects

    month_table = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    month_dict = {string: index+1 for index, string in enumerate(month_table)}

    print(month_dict)

    datetime_array = []

    for i in range(len(datetime_strings)):

        s = datetime_strings[i].split()

        dt = datetime.datetime(int(s[2]), month_dict[s[1]], int(s[0]), int(s[3].split(':')[0]), int(s[3].split(':')[1]))
        date = dt.date()
        time = dt.time()
        datetime_array.append([date,time])

    return np.array(datetime_array)

def get_top_n_artists(data_frame, n):

    #count up all the artists going through the dates one by one

    artist_table = data_frame['Artist'].unique()
    date_table = data_frame['Date'].unique()
    artist_counts = {}
    time_series = []
    current_date = data_frame.iloc[0]['Date'].isoformat()

    for i in range(data_frame.shape[0]-1):

        #scrobble = data_frame[data_frame['Date'] == date_table[i]].iloc[-1,]
        scrobble = data_frame.iloc[i]
        scrobble_1 = data_frame.iloc[i+1]

        if scrobble['Artist'] in artist_counts:
            artist_counts[scrobble['Artist']] += 1
        else:
            artist_counts[scrobble['Artist']] = 1

        artist_counter = Counter(artist_counts)
        top_n = artist_counter.most_common(n)

        if scrobble_1['Date'].isoformat() != current_date:
            for j in range(n):
                time_series.append([len(time_series), current_date, top_n[j][0], j+1])
            current_date = scrobble_1['Date'].isoformat()

    return np.array(time_series).squeeze()

def get_top_n(df, n, column):

    current_date = df.iloc[0]['Date']
    time_delta = datetime.timedelta(days=1)
    end_date = df.iloc[-1]['Date']
    counts = {}
    time_series = pd.DataFrame([current_date],columns=['Date'])

    while current_date <= end_date:

        row = [current_date] + [0]*(len(time_series.columns) - 1)
        row_df = pd.DataFrame([row], columns=time_series.columns)
        #row_df = time_series.iloc[-1]
        #row_df.at['Date'] = current_date
        time_series = time_series.append(row_df, ignore_index=True)

        scrobbles = df[df['Date'] == current_date]
        if not scrobbles.empty:

            unique = scrobbles[column].unique()
            for i in range(len(unique)):

                if unique[i] in counts:
                    counts[unique[i]] += len(scrobbles[scrobbles[column] == unique[i]])
                else:
                    counts[unique[i]] = len(scrobbles[scrobbles[column] == unique[i]])

            counter = Counter(counts)
            top_n = counter.most_common(n)

            #print(top_n)

            for i in range(n):
                #row_df[top_n[i][0]] = top_n[i][1]
                key = top_n[i][0]
                val = top_n[i][1]
                idx = len(time_series)-1
                if key not in time_series.columns:
                    time_series[key] = [0]*len(time_series)
                time_series.at[idx,key] = val

        else:
            time_series.iloc[-1,1:] = time_series.iloc[-2,1:]



        current_date = current_date + time_delta

    return time_series.iloc[1:]

def get_uniques_by_week(df):

    current_date = df.iloc[0]['Date']
    time_delta = datetime.timedelta(days=7)
    end_date = df.iloc[-1]['Date']
    time_series = pd.DataFrame(columns=['Date','Num_Artists','Num_Albums','Num_Tracks'])

    while current_date < end_date:

        week_scrobbles = pd.DataFrame(columns = df.columns)
        for i in range(7):
            date = current_date + datetime.timedelta(days=i)
            day_scrobbles = df[df['Date'] == date]
            if not day_scrobbles.empty:
                #print(day_scrobbles)
                week_scrobbles = week_scrobbles.append(day_scrobbles, ignore_index=True)
                #print(week_scrobbles)

        #start = df.index[df['Date'] == current_date].tolist()[0]
        #end = df.index[df['Date'] == current_date+time_delta].tolist()[0]

        #scrobbles = df.iloc[start:end,:]
        num_artists = len(week_scrobbles['Artist'].unique())
        num_albums = len(week_scrobbles['Album'].unique())
        num_tracks = len(week_scrobbles['Track'].unique())

        time_series = time_series.append(pd.DataFrame([[current_date,num_artists,num_albums,num_tracks]],columns=time_series.columns), ignore_index=True)

        current_date = current_date + time_delta

    return time_series

def get_total_uniques(df):

    current_date = df.iloc[0]['Date']
    time_delta = datetime.timedelta(days=1)
    end_date = df.iloc[-1]['Date']
    artist_dict = {}
    album_dict = {}
    track_dict = {}
    time_series = pd.DataFrame([[current_date,0,0,0,0]],columns=['Date','Num_Artists','Num_Albums','Num_Tracks','Num_Scrobbles'])
    total = [0,0,0,0]

    while current_date <= end_date:

        scrobbles = df[df['Date'] == current_date]
        num_artists = 0
        num_albums = 0
        num_tracks = 0
        num_scrobbles = 0
        if not scrobbles.empty:
            artists = scrobbles['Artist'].unique()
            for name in artists:
                if name not in artist_dict:
                    num_artists += 1
                    artist_dict[name] = 1
            albums = scrobbles['Album'].unique()
            for name in albums:
                if name not in album_dict:
                    num_albums += 1
                    album_dict[name] = 1
            tracks = scrobbles['Track'].unique()
            for name in tracks:
                if name not in track_dict:
                    num_tracks += 1
                    track_dict[name] = 1
            #num_artists = len(scrobbles['Artist'].unique())
            #num_albums = len(scrobbles['Album'].unique())
            #num_tracks = len(scrobbles['Track'].unique())
            num_scrobbles = len(scrobbles)

        total = [total[0]+num_artists,total[1]+num_albums,total[2]+num_tracks,total[3]+num_scrobbles]
        day_df = pd.DataFrame([[current_date] + total], columns=time_series.columns)

        time_series = time_series.append(day_df, ignore_index=True)

        current_date = current_date + time_delta

    return time_series


def get_timeseries(data_frame):

    # get number of artists, albums, songs listened to each day

    time_series = []
    time_delta = datetime.timedelta(days=1)
    current_date = data_frame.iloc[0]['Date']

    while current_date <= datetime.date.today():
        daily_scrobbles = data_frame[data_frame['Date'] == current_date]
        if daily_scrobbles.empty:
            time_series.append([current_date, 0, 0, 0])

            current_date = current_date + time_delta

        else:
            num_artists = len(daily_scrobbles['Artist'].unique())
            num_albums = len(daily_scrobbles['Album'].unique())
            num_scrobbles = daily_scrobbles.shape[0]

            time_series.append([current_date, num_artists, num_albums, num_scrobbles])

            current_date = current_date + time_delta

    time_series_pd = pd.DataFrame(time_series, columns=['Date','NumArtists','NumAlbums','NumScrobbles'])

    return time_series_pd

def moving_avg(data, window):
    ret = np.cumsum(data,dtype='float')
    ret[window:] = ret[window:] - ret[:-window]
    return ret[window-1:] / window

a = pd.read_csv('Pai-Sho.csv').dropna()

a['Date'] = parse_datetime(a['Datetime'].to_numpy())[:,0]
a['Time'] = parse_datetime(a['Datetime'].to_numpy())[:,1]
a = a.sort_values(by=['Date','Time'])

#print(a)

n = 10

#print(get_uniques_by_week(a))

#b = get_top_n(a, n, 'Artist')

#print(b)

#b.to_csv('test.csv')

'''
b = get_top_n_artists(a,n)

top10 = pd.DataFrame(b,columns=['Index','Date','Artist','Plays'])

alltop10 = top10['Artist'].unique()

yikes = pd.DataFrame(columns=alltop10)

artist_dict = {string:index+1 for index,string in enumerate(yikes)}

for i in range(0,len(top10),n):

    l = [0]*len(alltop10)

    for j in range(n):
        if i+j >= len(alltop10):
            break
        l[artist_dict[top10.iloc[i+j]['Artist']]] = top10.iloc[i+j]['Plays']

    lpd = pd.DataFrame([l], columns=alltop10)

    yikes = yikes.append(lpd, ignore_index=True)

yikes['Date'] = top10['Date']

print(yikes)

print(top10)
print(alltop10)
#print(len(top10['Artist'].unique()))

#ts = get_timeseries(a)
#
#print(ts)
'''

'''
fuck = moving_avg(ts['NumArtists'].to_numpy(),7)

p = figure(plot_width=1500,lod_threshold=None)


p.line(ts['Date'], ts['NumArtists'])
p.line(ts['Date'].to_numpy()[::7], fuck)
p.xaxis.formatter=DatetimeTickFormatter(
    hours=["%d %B %Y"],
    days=["%d %B %Y"],
    months=["%d %B %Y"],
    years=["%d %B %Y"],
)

show(p)
'''
n = 6
b = get_top_n(a,n,'Artist')
c = get_uniques_by_week(a)
d = get_total_uniques(a)

output_file = ("Pai-Sho.html")

print(d)

#b.to_csv('top_%d_artists.csv'%(n))

#b = pd.read_csv('top_10_artists.csv')

print(b.index[b['Date'] == datetime.date(2016,1,1)].tolist())

start = b.index[b['Date'] == datetime.date(2016,1,1)].tolist()[0]

b = b.iloc[start:,:]

print(b)

b.iloc[:,1:] = b.iloc[:,1:].div(b.sum(axis=1), axis=0)
b = b.fillna(0)


b = b.loc[:, (b != 0).any(axis=0)]

N = len(b.columns) - 1
print(N)
print(b)





#labels = LabelSet(x='Date', y='height', text='names', level='glyph',
#              x_offset=5, y_offset=5, source=source, render_mode='canvas')

#daylight_savings_start = Span(location=start_date,
#                              dimension='height', line_color='green',
#                              line_dash='dashed', line_width=3)
#p.add_layout(daylight_savings_start)

annotation_dates = [    datetime.date(2016,8,24),
                        datetime.date(2016,9,27),
                        datetime.date(2017,1,1),
                        datetime.date(2017,4,14),
                        datetime.date(2017,8,14),
                        datetime.date(2018,1,26),
                        datetime.date(2018,5,20),
                        datetime.date(2018,8,3),
                        datetime.date(2019,1,4),
                        datetime.date(2019,4,9),
                        datetime.date(2019,5,20),
                        datetime.date(2019,7,28),
                        datetime.date(2019,8,16)]
annotation_labels = [   "Moved to Houston to begin NASA internship",
                        "Danny Brown releases Atrocity Exhibition",
                        "Transitioned to NASA Pathways Program",
                        "Kendrick Lamar releases DAMN",
                        "Moved Back to Minnesota to finish Undergrad",
                        "Migos release Culture II",
                        "Returned to Houston for Summer/Fall rotation",
                        "Travis Scott releases Astroworld",
                        "Moved to Colorado",
                        "Ended long-term relationship",
                        "Returned to Houston for Summer rotation",
                        "Returned to Colorado to begin Grad School full-time",
                        "Young Thug releases So Much Fun"]

annotations = ColumnDataSource(data=dict(annotation_dates=annotation_dates,
                                    annotation_labels=annotation_labels))

spans = []

for i in range(len(annotation_dates)):
    spans.append(Span(location=annotation_dates[i],dimension='height',line_color='black',line_width=3,line_alpha=0.3))




h = HoverTool(
    names=['art'],
    tooltips=[
        ( 'Date',   '@Date{%F}'            ),
        ( 'Num Artists',  '@Num_Artists{%d}' ), # use @{ } for field names with spaces
        ( 'Num Albums', '@Num_Albums{%d}'      ),
        ( 'Num Tracks', '@Num_Tracks{%d}'      ),
    ],

    formatters={
        'Date'      : 'datetime', # use 'datetime' formatter for 'date' field
        'Num_Artists': 'printf',
        'Num_Albums': 'printf',
        'Num_Tracks': 'printf',
    },

    # display a tooltip whenever the cursor is vertically in line with a glyph
    mode='vline'
)

ht = HoverTool(
    names=["events"],
    tooltips=[
        ('Date','@annotation_dates{%F}'),
        ('Event','@annotation_labels')
    ],
    formatters={
        'annotation_dates':'datetime',
    },
    mode='vline'
)

p = figure(plot_width=1500, plot_height=350,x_axis_type="datetime",x_range=(b.iloc[0]['Date'], b.iloc[-1]['Date']), tools=[ht,"xpan"], toolbar_location=None)
p.grid.minor_grid_line_color = '#eeeeee'

names = list(b.columns[1:])
print(names)

fffuck = ['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c', '#98df8a', '#d62728', '#ff9896', '#9467bd', '#c5b0d5', '#8c564b', '#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f', '#c7c7c7', '#bcbd22', '#dbdb8d', '#17becf', '#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c', '#98df8a', '#d62728', '#ff9896', '#9467bd', '#c5b0d5', '#8c564b', '#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f', '#c7c7c7', '#bcbd22', '#dbdb8d', '#17becf', '#9edae5', '#ffbb78']
lotta_colors = ["#000000","#FFFF00","#1CE6FF","#FF34FF","#FF4A46","#008941","#006FA6","#A30059","#FFDBE5","#7A4900","#0000A6","#63FFAC","#B79762","#004D43","#8FB0FF","#997D87","#5A0007","#809693","#FEFFE6","#1B4400","#4FC601","#3B5DFF","#4A3B53","#FF2F80","#61615A","#BA0900","#6B7900","#00C2A0","#FFAA92","#FF90C9","#B903AA","#D16100","#DDEFFF","#000035","#7B4F4B","#A1C299","#300018","#0AA6D8","#013349","#00846F","#372101","#FFB500","#C2FFED","#A079BF","#CC0744","#C0B9B2","#C2FF99","#001E09","#00489C","#6F0062","#0CBD66","#EEC3FF","#456D75","#B77B68","#7A87A1","#788D66","#885578","#FAD09F","#FF8A9A","#D157A0","#BEC459","#456648","#0086ED","#886F4C","#34362D","#B4A8BD","#00A6AA","#452C2C","#636375","#A3C8C9","#FF913F","#938A81","#575329","#00FECF","#B05B6F","#8CD0FF","#3B9700","#04F757","#C8A1A1","#1E6E00","#7900D7","#A77500","#6367A9","#A05837","#6B002C","#772600","#D790FF","#9B9700","#549E79","#FFF69F","#201625","#72418F","#BC23FF","#99ADC0","#3A2465","#922329","#5B4534","#FDE8DC","#404E55","#0089A3","#CB7E98","#A4E804","#324E72","#6A3A4C","#83AB58","#001C1E","#D1F7CE","#004B28","#C8D0F6","#A3A489","#806C66","#222800","#BF5650","#E83000","#66796D","#DA007C","#FF1A59","#8ADBB4","#1E0200","#5B4E51","#C895C5","#320033","#FF6832","#66E1D3","#CFCDAC","#D0AC94","#7ED379","#012C58","#7A7BFF","#D68E01","#353339","#78AFA1","#FEB2C6","#75797C","#837393","#943A4D","#B5F4FF","#D2DCD5","#9556BD","#6A714A","#001325","#02525F","#0AA3F7","#E98176","#DBD5DD","#5EBCD1","#3D4F44","#7E6405","#02684E","#962B75","#8D8546","#9695C5","#E773CE","#D86A78","#3E89BE","#CA834E","#518A87","#5B113C","#55813B","#E704C4","#00005F","#A97399","#4B8160","#59738A","#FF5DA7","#F7C9BF","#643127","#513A01","#6B94AA","#51A058","#A45B02","#1D1702","#E20027","#E7AB63","#4C6001","#9C6966","#64547B","#97979E","#006A66","#391406","#F4D749","#0045D2","#006C31","#DDB6D0","#7C6571","#9FB2A4","#00D891","#15A08A","#BC65E9","#FFFFFE","#C6DC99","#203B3C","#671190","#6B3A64","#F5E1FF","#FFA0F2","#CCAA35","#374527","#8BB400","#797868","#C6005A","#3B000A","#C86240","#29607C","#402334","#7D5A44","#CCB87C","#B88183","#AA5199","#B5D6C3","#A38469","#9F94F0","#A74571","#B894A6","#71BB8C","#00B433","#789EC9","#6D80BA","#953F00","#5EFF03","#E4FFFC","#1BE177","#BCB1E5","#76912F","#003109","#0060CD","#D20096","#895563","#29201D","#5B3213","#A76F42","#89412E","#1A3A2A","#494B5A","#A88C85","#F4ABAA","#A3F3AB","#00C6C8","#EA8B66","#958A9F","#BDC9D2","#9FA064","#BE4700","#658188","#83A485","#453C23","#47675D","#3A3F00","#061203","#DFFB71","#868E7E","#98D058","#6C8F7D","#D7BFC2","#3C3E6E","#D83D66","#2F5D9B","#6C5E46","#D25B88","#5B656C","#00B57F","#545C46","#866097","#365D25","#252F99","#00CCFF","#674E60","#FC009C","#92896B"]


p.varea_stack(stackers=names, x='Date', color=fffuck[:N], source=b)
#p.legend.location = (1501,350)
p.xaxis.formatter=DatetimeTickFormatter(
    hours=["%d %B %Y"],
    days=["%d %B %Y"],
    months=["%d %B %Y"],
    years=["%d %B %Y"],
)

p2 = figure(plot_width=1500, plot_height=350,x_axis_type="datetime",x_range=p.x_range, tools=[h,"xpan"], toolbar_location=None)
p2.line(x='Date',y='Num_Artists',source=c,line_width=3,line_color=Category20[6][0],legend_label='Num_Artists')
p2.line(x='Date',y='Num_Albums',source=c,line_width=3,line_color=Category20[6][2],legend_label='Num_Albums')
p2.line(x='Date',y='Num_Tracks',source=c,line_width=3,line_color=Category20[6][4],legend_label='Num_Tracks',name="art")
p.circle(x='annotation_dates',y=1,source=annotations,line_alpha=0,fill_alpha=0,name="events",radius=8)

p3 = figure(plot_width=1500, plot_height=350,x_axis_type="datetime",x_range=p.x_range, tools=[h,"xpan"], toolbar_location=None)
p3.line(x='Date',y='Num_Artists',source=d,line_width=3,line_color=Category20[6][0],legend_label='Num_Artists')
p3.line(x='Date',y='Num_Albums',source=d,line_width=3,line_color=Category20[6][2],legend_label='Num_Albums')
p3.line(x='Date',y='Num_Tracks',source=d,line_width=3,line_color=Category20[6][4],legend_label='Num_Tracks',name='art')
#p3.circle(x='annotation_dates',y=600,source=annotations,line_alpha=0,fill_alpha=0,name="events")

select = figure(title="Drag the middle and edges of the selection box to change the date range of the plots below",
                plot_height=130, plot_width=1500, y_range=p.y_range,
                x_axis_type="datetime", y_axis_type=None,
                tools="", toolbar_location=None, background_fill_color="#efefef")

range_tool = RangeTool(x_range=p.x_range)
range_tool.overlay.fill_color = "navy"
range_tool.overlay.fill_alpha = 0.2

select.varea_stack(stackers=names, x='Date', color=fffuck[:N], source=b)
select.ygrid.grid_line_color = None
select.add_tools(range_tool)
select.toolbar.active_multi = range_tool
p2.xaxis.formatter=DatetimeTickFormatter(
    hours=["%d %B %Y"],
    days=["%d %B %Y"],
    months=["%d %B %Y"],
    years=["%d %B %Y"],
)
p3.xaxis.formatter=DatetimeTickFormatter(
    hours=["%d %B %Y"],
    days=["%d %B %Y"],
    months=["%d %B %Y"],
    years=["%d %B %Y"],
)
p2.legend.location='top_left'
p3.legend.location='top_left'

p.title.text = "Normalized Top-6 All-Time Artists"
p2.title.text = "Unique Artists, Albums and Tracks Listened by Week"
p3.title.text = "Total Unique Artists, Albums and Tracks Listened over Time"

for i in range(len(spans)):
    p.add_layout(spans[i])
    p2.add_layout(spans[i])
    p3.add_layout(spans[i])


legend = Legend(items=[])

show(column(select, p, p2, p3))

'''
p1 = figure(plot_width=1500, plot_height=1000, title="The Likeability of Art across Time and Style", lod_threshold=None)

source = ColumnDataSource(data=dict(
        x = top10['Index'],
        artist = top10['Artist'],
        y = top10['Plays'],
    ))

p1.circle('x', 'y', size=3, source=source)

show(p1)
'''
