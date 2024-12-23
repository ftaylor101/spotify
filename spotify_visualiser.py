import pandas as pd
import plotly.express as px
import streamlit as st


st.title(":notes: Visualise your Spotify data :bar_chart:")

uploaded_file = st.file_uploader("Add your data", accept_multiple_files=True)
if uploaded_file:
    if isinstance(uploaded_file, list):
        df = pd.DataFrame()
        for file in uploaded_file:
            tmp_df = pd.read_json(file)
            df = pd.concat([tmp_df, df], axis=0)
        df_created = True
    else:
        df = pd.read_json(uploaded_file)
        df_created = True
else:
    df_created = False

if df_created:
    # df = pd.read_json(uploaded_file)
    df["datetime"] = pd.to_datetime(df["ts"], format="%Y-%m-%dT%H:%M:%SZ")
    df["dayname"] = df["datetime"].dt.day_name()
    df["hour"] = df["datetime"].dt.hour
    df["month"] = df["datetime"].dt.month_name()
    df["master_metadata_track_name"] = df["master_metadata_track_name"] + " | " + df["master_metadata_album_artist_name"]
    st.dataframe(df.head())

    st.write("### Select Date Range")
    min_date = df["datetime"].min().date()
    max_date = df["datetime"].max().date()
    start_date, end_date = st.date_input("Date range", [min_date, max_date], min_value=min_date, max_value=max_date)

    mask = (df["datetime"].dt.date >= start_date) & (df["datetime"].dt.date <= end_date)
    df_date_filtered = df[mask]

    st.write("### Overall Stats :bar_chart:")
    top_artist = df_date_filtered["master_metadata_album_artist_name"].mode()[0]
    top_album = df_date_filtered["master_metadata_album_album_name"].mode()[0]
    top_track = df_date_filtered["master_metadata_track_name"].mode()[0]

    overall_stats = {
        "Category": ["Top Artist", "Top Album", "Top Track"],
        "Name": [top_artist, top_album, top_track]
    }
    overall_stats_df = pd.DataFrame(overall_stats)
    st.table(overall_stats_df)

    st.write("### Platforms :desktop_computer: :iphone: :video_game: :tv:")
    os_fig = px.histogram(df_date_filtered, x="platform")
    st.plotly_chart(os_fig)

    st.write("## More charts")
    st.write("Below are charts that show the artists/albums/tracks that make up the top 25/50/75/100% of all the music listened to.")
    # artist
    st.write("### Artists :female-singer: 	:microphone:")
    artist_filter = st.selectbox("Top %", [25, 50, 75, 100], index=3, key="artist_filter")
    if artist_filter == 100:
        artists_fig = px.histogram(df_date_filtered, x="master_metadata_album_artist_name")
        st.plotly_chart(artists_fig)
    else:
        artist_listens_cumulative_df = df_date_filtered["master_metadata_album_artist_name"].value_counts().cumsum()
        listen_count = artist_listens_cumulative_df.max() * (artist_filter/100)
        filtered_artists = artist_listens_cumulative_df[artist_listens_cumulative_df < listen_count].index.values
        filtered_df = df_date_filtered[df_date_filtered["master_metadata_album_artist_name"].isin(filtered_artists)]
        artists_fig = px.histogram(filtered_df, x="master_metadata_album_artist_name")
        st.plotly_chart(artists_fig)

    # album
    st.write("### Albums	:minidisc:")
    album_filter = st.selectbox("Top %", [25, 50, 75, 100], index=3, key="album_filter")
    if album_filter == 100:
        album_fig = px.histogram(df_date_filtered, x="master_metadata_album_album_name")
        st.plotly_chart(album_fig)
    else:
        album_listens_cumulative_df = df_date_filtered["master_metadata_album_album_name"].value_counts().cumsum()
        listen_count = album_listens_cumulative_df.max() * (album_filter/100)
        filtered_album = album_listens_cumulative_df[album_listens_cumulative_df < listen_count].index.values
        filtered_df = df_date_filtered[df_date_filtered["master_metadata_album_album_name"].isin(filtered_album)]
        album_fig = px.histogram(filtered_df, x="master_metadata_album_album_name")
        st.plotly_chart(album_fig)

    # track
    st.write("### Tracks :musical_score:")
    track_filter = st.selectbox("Top %", [25, 50, 75, 100], index=3, key="track_filter")
    if track_filter == 100:
        track_fig = px.histogram(df_date_filtered, x="master_metadata_track_name")
        st.plotly_chart(track_fig)
    else:
        track_listens_cumulative_df = df_date_filtered["master_metadata_track_name"].value_counts().cumsum()
        listen_count = track_listens_cumulative_df.max() * (track_filter/100)
        filtered_track = track_listens_cumulative_df[track_listens_cumulative_df < listen_count].index.values
        filtered_df = df_date_filtered[df_date_filtered["master_metadata_track_name"].isin(filtered_track)]
        track_fig = px.histogram(filtered_df, x="master_metadata_track_name")
        st.plotly_chart(track_fig)

    # countries
    st.write("### Countries :world_map:")
    st.write("Unfortunately I can't find the code to country name so I can't convert to countries and the plot them on a map.")
    st.dataframe(df_date_filtered["conn_country"].unique())

    # listening stats
    st.write("### Time :stopwatch: :hourglass_flowing_sand:")

    # most popular hour of the day
    hours_df = df_date_filtered.groupby(["hour"])
    songs_per_hour_df = hours_df["hour"].value_counts().to_frame()
    songs_per_hour_df.reset_index(inplace=True)
    songs_per_hour_fig = px.bar(songs_per_hour_df, x="hour", y="count", title="Total number of songs played each hour across listening history")
    st.plotly_chart(songs_per_hour_fig)

    # hours per day
    days_df = df_date_filtered.groupby(["dayname"])
    hours_per_day_df = days_df["ms_played"].sum().to_frame()
    hours_per_day_df.reset_index(inplace=True)
    hours_per_day_df["hours"] = hours_per_day_df["ms_played"]/3600000
    hours_per_day_fig = px.bar(hours_per_day_df, x='dayname', y='hours', title="Time in hours listened per day across entire listening history")
    st.plotly_chart(hours_per_day_fig)

    # monthly listening time
    months_df = df_date_filtered.groupby(["month"])
    songs_per_month_df = months_df["month"].value_counts().to_frame()
    songs_per_month_df.reset_index(inplace=True)
    songs_per_month_fig = px.bar(songs_per_month_df, x="month", y="count", title="Total number of songs played each month across listening history")
    st.plotly_chart(songs_per_month_fig)
