# import library yang dibutuhkan
import pandas as pd
import datetime
import numpy as np
from bokeh.io import curdoc
from bokeh.plotting import figure, show
from bokeh.models import HoverTool, ColumnDataSource, LinearColorMapper, ColorBar, BasicTicker
from bokeh.palettes import Spectral11
from bokeh.models import Slider, Select, Column, Row
from bokeh.protocol import push_doc
from bokeh.transform import transform

df = pd.read_csv("online_retail_2.csv")
df["InvoiceNo"] = df["InvoiceNo"].apply(lambda x: str(x))
df["InvoiceDate"] = df["InvoiceDate"].apply(lambda x : datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S"))
df["Country"] = df["Country"].apply(lambda x: str(x))

df["date"] = pd.DatetimeIndex(df['InvoiceDate']).date
df["date"] = df["date"].apply(lambda x: int(x.strftime("%d")))

df["month"] = pd.DatetimeIndex(df['InvoiceDate']).month
df["year"] = pd.DatetimeIndex(df['InvoiceDate']).year

df["hour"] = df["InvoiceDate"].apply(lambda x : x.strftime("%H"))

df_week = df.copy(deep=True)
df_week = df_week.loc[df["year"] == 2011]
df_week = df_week.loc[df["month"] == 1]
df_week = df_week.loc[df["date"] >= 3]
df_week = df_week.loc[df["date"] <= 9]

df_week["date"] = df_week["date"].astype("str")
df_week["hour"] = df_week["hour"].astype("int")

dates = df_week.date.unique()
hours = df_week.hour.unique().tolist()

hours.sort()

dates_in_int = []
for date in dates:
    dates_in_int.append(int(date))

dates_in_int.insert(0, '3')
dates_in_int.insert(5, '8')

dates_in_int = [date for date in dates_in_int]
dates = []
for date in dates_in_int:
    dates.append(str(date))

d = {}
for date in dates:
    d[date] = []
    for hour in hours:
        df_subset = df_week.copy(deep=True)
        df_subset = df_subset[(df_subset["date"] == date) & (df_subset["hour"] == hour)]
        d[date].append(len(df_subset.InvoiceNo.unique()))

d["hour"] = hours
matriks_date_hour = pd.DataFrame(data=d)
matriks_date_hour["hour"] = matriks_date_hour["hour"].astype("str")
matriks_date_hour = matriks_date_hour.set_index("hour")
matriks_date_hour.columns.name = "date"

df_week = pd.DataFrame(matriks_date_hour.stack(), columns=["frequency"]).reset_index()
source = ColumnDataSource(df_week)

mapper = LinearColorMapper(palette=Spectral11, low=df_week.frequency.min(), high=df_week.frequency.max())

p = figure(
    width=1080,
    height=400,
    title="Frekuensi Transaksi",
    x_range=list(matriks_date_hour.columns),
    y_range=list(matriks_date_hour.index),
    toolbar_location=None,
    tools="",
    x_axis_location="below",
    x_axis_label = "Tanggal",
    y_axis_label="Jam",
    name='plot'
)

p.rect(
    x="date",
    y="hour",
    width=1,
    height=1,
    source=source,
    line_color=None,
    fill_color=transform('frequency', mapper)
)

color_bar = ColorBar(
    color_mapper=mapper,
    ticker=BasicTicker(desired_num_ticks=len(Spectral11))
)

p.add_layout(color_bar, 'right')

def update_plot(attr, old, new):
    no_week = slider_week.value
    country = select_country.value

    new_df = df.copy(deep=True)

    first_date = datetime.date(2010, 12, 27) + datetime.timedelta(days=7*no_week)
    last_date = datetime.date(2011, 1, 3) + datetime.timedelta(days=7*no_week)

    first_date = np.datetime64(first_date)
    last_date = np.datetime64(last_date)

    new_df = new_df[new_df["InvoiceDate"] >= first_date]
    new_df = new_df[new_df["InvoiceDate"] <= last_date]

    if country != "Semua":
        new_df = new_df[new_df["Country"] == country]

    df_week = new_df.copy(deep=True)
    # print(len(df_week))

    dates = []
    hours = []

    if len(df_week)!=0:
        df_week["date"] = df_week["date"].astype("str")
        df_week["hour"] = df_week["hour"].astype("int")

        dates = df_week.date.unique()
        hours = df_week.hour.unique().tolist()
        hours.sort()

        dates_in_int = []
        for date in dates:
            dates_in_int.append(int(date))
        dates_in_int = range(min(dates_in_int), max(dates_in_int) + 1)
        dates_in_int = [date for date in dates_in_int]

        dates_in_int.sort()
        while len(dates_in_int)!=7:
            dates_in_int.append(max(dates_in_int)+1)

        dates = []
        for date in dates_in_int:
            dates.append(str(date))

        if no_week == 1:
            dates = ['3', '4', '5', '6', '7', '8', '9']

    d = {}
    for date in dates:
        d[date] = []
        for hour in hours:
            df_subset = df_week.copy(deep=True)
            df_subset = df_subset[(df_subset["date"] == date) & (df_subset["hour"] == hour)]
            d[date].append(len(df_subset.InvoiceNo.unique()))

    d["hour"] = hours
    matriks_date_hour = pd.DataFrame(data=d)
    matriks_date_hour["hour"] = matriks_date_hour["hour"].astype("str")
    matriks_date_hour = matriks_date_hour.set_index("hour")
    matriks_date_hour.columns.name = "date"

    df_week = pd.DataFrame(matriks_date_hour.stack(), columns=["frequency"]).reset_index()

    source_inner = ColumnDataSource(df_week)

    p_new = figure(
        width=1080,
        height=400,
        title="Frekuensi Transaksi",
        x_range=list(matriks_date_hour.columns),
        y_range=list(matriks_date_hour.index),
        toolbar_location=None,
        tools="",
        x_axis_location="below",
        x_axis_label="Tanggal",
        y_axis_label="Jam",
        name="plot"
    )
    p_new.rect(
        x="date",
        y="hour",
        width=1,
        height=1,
        source=source_inner,
        line_color=None,
        fill_color=transform('frequency', mapper)
    )

    color_bar = ColorBar(
        color_mapper=mapper,
        ticker=BasicTicker(desired_num_ticks=len(Spectral11))
    )

    p_new.add_layout(color_bar, 'right')

    rootLayout = curdoc().get_model_by_name('mainLayout')
    listOfSubLayouts = rootLayout.children
    plotToRemove = curdoc().get_model_by_name('plot')
    listOfSubLayouts.remove(plotToRemove)
    listOfSubLayouts.append(p_new)

slider_week = Slider(start=1, end=4, step=1, value=1, title="Minggu ke-")
slider_week.on_change('value', update_plot)

countries = ["Semua"] + df["Country"].unique().tolist()

select_country = Select(
    options=countries,
    value='Semua',
    title='Negara'
)
select_country.on_change('value', update_plot)

layout = Column(Row(slider_week, select_country), p, name='mainLayout')
curdoc().add_root(layout)
