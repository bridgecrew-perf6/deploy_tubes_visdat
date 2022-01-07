# import library yang dibutuhkan
import pandas as pd
import datetime
import numpy as np
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, LinearColorMapper, ColorBar, BasicTicker
from bokeh.models import Slider, Select, Column, Row
from bokeh.transform import transform

df = pd.read_csv("online_retail_2.csv") # Membaca data

# Mengubah tipe data
df["InvoiceNo"] = df["InvoiceNo"].apply(lambda x: str(x))  # tipe data object diubah menjadi tipe data string
df["InvoiceDate"] = df["InvoiceDate"].apply(lambda x : datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S"))  # tipe data object diubah menjadi tipe data datetime
df["Country"] = df["Country"].apply(lambda x: str(x))  # tipe data object diubah menjadi tipe data string

df["date"] = pd.DatetimeIndex(df['InvoiceDate']).date  # membuat kolom date bertipe datetime.date
df["date"] = df["date"].apply(lambda x: int(x.strftime("%d")))  # mengambil tanggal (1-31) dari sebuah nilai datetime.date

df["month"] = pd.DatetimeIndex(df['InvoiceDate']).month  # membuat kolom month
df["year"] = pd.DatetimeIndex(df['InvoiceDate']).year  # membuat kolom year

df["hour"] = df["InvoiceDate"].apply(lambda x : x.strftime("%H"))  # membuat kolom hour

df_week = df.copy(deep=True)  # copy dataframe

# filter dataframe sampai hanya tersisa data dari tanggal 3-1-2011 sampai 9-1-2011 (minggu pertama)
df_week = df_week.loc[df["year"] == 2011]
df_week = df_week.loc[df["month"] == 1]
df_week = df_week.loc[df["date"] >= 3]
df_week = df_week.loc[df["date"] <= 9]

# Mengubah tipe data
df_week["date"] = df_week["date"].astype("str")
df_week["hour"] = df_week["hour"].astype("int")

# Mengambil tanggal dan jam transaksi
dates = df_week.date.unique()
hours = df_week.hour.unique().tolist()

hours.sort()  # Mengurutkan jam

# Menambah tanggal 3 dan 8
dates_in_int = []
for date in dates:
    dates_in_int.append(int(date))
dates_in_int.insert(0, '3')
dates_in_int.insert(5, '8')
dates_in_int = [date for date in dates_in_int]
dates = []
for date in dates_in_int:
    dates.append(str(date))

# Membuat data untuk matriks_date_hour
d = {}
for date in dates:
    d[date] = []
    for hour in hours:
        df_subset = df_week.copy(deep=True)
        df_subset = df_subset[(df_subset["date"] == date) & (df_subset["hour"] == hour)]
        d[date].append(len(df_subset.InvoiceNo.unique()))

# Membat matriks_date_hour
d["hour"] = hours
matriks_date_hour = pd.DataFrame(data=d)
matriks_date_hour["hour"] = matriks_date_hour["hour"].astype("str")
matriks_date_hour = matriks_date_hour.set_index("hour")
matriks_date_hour.columns.name = "date"

# Membuat source sebagai data yang akan diplotting
df_week = pd.DataFrame(matriks_date_hour.stack(), columns=["frequency"]).reset_index()
source = ColumnDataSource(df_week)

# Membuat mapper
colors = [
    "#ffffd3",
    "#fbf6bf",
    "#f8ecab",
    "#f6e298",
    "#f5d785",
    "#f4cc72",
    "#f5c060",
    "#f5b44f",
    "#f6a73f",
    "#f7992f",
    "#f98b1f",
    "#fa7b10",
    "#fc6a01",
    "#fd5500",
    "#fe3b00",
    "#ff0000"
]
mapper = LinearColorMapper(palette=colors, low=df_week.frequency.min(), high=df_week.frequency.max())

# Membuat figure
p = figure(
    width=720,
    height=400,
    title="Heatmap Transaksi Minggu ke-1 (Semua Negara)",
    x_range=list(matriks_date_hour.columns),
    y_range=list(matriks_date_hour.index),
    toolbar_location=None,
    tools="",
    x_axis_location="below",
    x_axis_label = "Tanggal",
    y_axis_label="Jam",
    name='plot'
)

# Membat heatmap
p.rect(
    x="date",
    y="hour",
    width=1,
    height=1,
    source=source,
    line_color=None,
    fill_color=transform('frequency', mapper)
)

# Membuat color bar
color_bar = ColorBar(
    color_mapper=mapper,
    ticker=BasicTicker(desired_num_ticks=16)
)
p.add_layout(color_bar, 'right')  # memposisikan color bar di sebelah kanan

# Fungsi callback yang dijalankan ketika nilai slider atau select berubah
def update_plot(attr, old, new):
    no_week = slider_week.value  # Mengambil nilai slider_week
    country = select_country.value  # Mengambil nilai select_country

    title = "Heatmap Transaksi Minggu ke-" + str(no_week)  # title heatmap

    new_df = df.copy(deep=True)  # copy dataframe

    first_date = datetime.date(2010, 12, 27) + datetime.timedelta(days=7*no_week)  # tanggal pertama di week yang sedang dipilih
    last_date = datetime.date(2011, 1, 3) + datetime.timedelta(days=7*no_week)  # tanggal pertama di week yang sedang dipilih

    # Convert first_date dan last_date menjadi tipe datetime64
    first_date = np.datetime64(first_date)
    last_date = np.datetime64(last_date)

    # filter dataframe agar hanya menyisakan data di minggu yang dipilih
    new_df = new_df[new_df["InvoiceDate"] >= first_date]
    new_df = new_df[new_df["InvoiceDate"] <= last_date]

    if country != "Semua":  # jika memilih semua country
        new_df = new_df[new_df["Country"] == country]  # filter dataframe agar hanya menyisakan data negara yang dipilih
        title = title + f' (Negara {country})'  # Menambah keterangan negara yang bersangkutan
    else:  # jika hanya memilih satu country
        title = title + " (Semua Negara)"  # Menambah keterangan negara

    df_week = new_df.copy(deep=True)  # copy dataframe

    dates = []  # akan diisi dengan tanggal-tanggal dari minggu yang dipilih
    hours = []  # akan diisi dengan jam-jam terjadinya transaksi di minggu yang dipilih

    # Cek apakah ada transaksi di negara yang dipilih di minggu yang dipilih
    if len(df_week)!=0:

        # Mengubah tipe data
        df_week["date"] = df_week["date"].astype("str")
        df_week["hour"] = df_week["hour"].astype("int")

        # Mengambil tanggal dan jam transaksi pada minggu yang dipilih
        dates = df_week.date.unique()
        hours = df_week.hour.unique().tolist()
        hours.sort()

        # Melengkapi tanggal yang kosong
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

        # Jika minggu pertama
        if no_week == 1:
            dates = ['3', '4', '5', '6', '7', '8', '9']

    # Membuat data untuk matriks_date_hour
    d = {}
    for date in dates:
        d[date] = []
        for hour in hours:
            df_subset = df_week.copy(deep=True)
            df_subset = df_subset[(df_subset["date"] == date) & (df_subset["hour"] == hour)]
            d[date].append(len(df_subset.InvoiceNo.unique()))

    # Membuat matriks_date_hour
    d["hour"] = hours
    matriks_date_hour = pd.DataFrame(data=d)
    matriks_date_hour["hour"] = matriks_date_hour["hour"].astype("str")
    matriks_date_hour = matriks_date_hour.set_index("hour")
    matriks_date_hour.columns.name = "date"

    # Membuat source sebagai data yang akan diplotting
    df_week = pd.DataFrame(matriks_date_hour.stack(), columns=["frequency"]).reset_index()
    source_inner = ColumnDataSource(df_week)

    # Membuat figure
    p_new = figure(
        width=720,
        height=400,
        title=title,
        x_range=list(matriks_date_hour.columns),
        y_range=list(matriks_date_hour.index),
        toolbar_location=None,
        tools="",
        x_axis_location="below",
        x_axis_label="Tanggal",
        y_axis_label="Jam",
        name="plot"
    )

    # Membuat heatmap
    p_new.rect(
        x="date",
        y="hour",
        width=1,
        height=1,
        source=source_inner,
        line_color=None,
        fill_color=transform('frequency', mapper)
    )

    # Membuat color bar
    color_bar = ColorBar(
        color_mapper=mapper,
        ticker=BasicTicker(desired_num_ticks=16)
    )
    p_new.add_layout(color_bar, 'right')  # Memposisikan color bar di kanan plot

    # Menghapus current plot dari tampilan, kemudian menampilkan plot baru
    rootLayout = curdoc().get_model_by_name('mainLayout')
    listOfSubLayouts = rootLayout.children
    plotToRemove = curdoc().get_model_by_name('plot')
    listOfSubLayouts.remove(plotToRemove)
    listOfSubLayouts.append(p_new)

# Membuat slider week, ada 4 wee yang dapat dipilih
slider_week = Slider(start=1, end=4, step=1, value=1, title="Minggu ke-")
slider_week.on_change('value', update_plot)  # menambahkan on change listener. Jika nilai slider berubah, maka program menjalankan fungsi update_plot

# Membuat select untuk memilih country
countries = ["Semua"] + df["Country"].unique().tolist()
select_country = Select(
    options=countries,
    value='Semua',
    title='Negara'
)
select_country.on_change('value', update_plot)  # menambahkan on change listener. Jika nilai select berubah, maka program menjalankan fungsi update_plot

layout = Column(Row(slider_week, select_country), p, name='mainLayout')  # Membuat layout yang menampung slider, select dan heatmap
curdoc().add_root(layout)  # Menampilkan layout
