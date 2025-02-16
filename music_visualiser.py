import pandas as pd
import plotly.express as px
import streamlit as st
from spotify_parser import SpotifyParser
from apple_parser import AppleParser


st.title(":notes: :eyes: :musical_note: :bar_chart:")

spotify_uploaded_files = st.file_uploader("Add Spotify data", accept_multiple_files=True)
apple_uploaded_files = st.file_uploader("Add Apple data", accept_multiple_files=True)
if spotify_uploaded_files:
    if isinstance(spotify_uploaded_files, list):
        df = pd.DataFrame()
        for file in spotify_uploaded_files:
            tmp_df = SpotifyParser(file).get_dataframe()
            df = pd.concat([tmp_df, df], axis=0)
        df_created = True
    else:
        df = SpotifyParser(spotify_uploaded_files).get_dataframe()
        df_created = True
elif apple_uploaded_files:
    # find order of files
    names = [apple_uploaded_files[i].name for i in range(len(apple_uploaded_files))]
    for i in range(len(apple_uploaded_files)):
        play_activity_idx = next(i for i, name in enumerate(names) if "Apple Music Play Activity" in name)
        library_tracks_idx = next(i for i, name in enumerate(names) if "Apple Music Library Tracks" in name)
        play_history_daily_tracks_idx = next(i for i, name in enumerate(names) if "Play History Daily Tracks" in name)
    st.write(f"The indexes are: {play_activity_idx, library_tracks_idx, play_history_daily_tracks_idx}")
    df = AppleParser(
        csv_file_path=apple_uploaded_files[play_activity_idx],
        library_tracks_file_path=apple_uploaded_files[library_tracks_idx],
        history_daily_tracks=apple_uploaded_files[play_history_daily_tracks_idx]
    ).get_dataframe()
    df_created = True
else:
    df_created = False

if df_created:
    st.dataframe(df.head())
    st.write(df.describe())

    st.write("### Select Date Range")
    min_date = df["Datetime"].min().date()
    max_date = df["Datetime"].max().date()
    start_date, end_date = st.date_input("Date range", [min_date, max_date], min_value=min_date, max_value=max_date)

    mask = (df["Datetime"].dt.date >= start_date) & (df["Datetime"].dt.date <= end_date)
    df_date_filtered = df[mask]

    st.write("### Overall Stats :bar_chart:")
    top_artist = df_date_filtered["Artist"].mode()[0]
    top_album = df_date_filtered["Album name"].mode()[0]
    top_track = df_date_filtered["Song and Artist name"].mode()[0]

    overall_stats = {
        "Category": ["Top Artist", "Top Album", "Top Track"],
        "Name": [top_artist, top_album, top_track]
    }
    overall_stats_df = pd.DataFrame(overall_stats)
    st.table(overall_stats_df)

    st.write("### Platforms :desktop_computer: :iphone: :video_game: :tv:")
    os_fig = px.histogram(df_date_filtered, x="Platform")
    st.plotly_chart(os_fig)

    st.write("## More charts")
    st.write("Below are charts that show the artists/albums/tracks that make up the top 25/50/75/100% of all the music listened to.")
    # artist
    st.write("### Artists :female-singer: 	:microphone:")
    artist_filter = st.selectbox("Top %", [25, 50, 75, 100], index=3, key="artist_filter")
    if artist_filter == 100:
        artists_fig = px.histogram(df_date_filtered, x="Artist")
        st.plotly_chart(artists_fig)
    else:
        artist_listens_cumulative_df = df_date_filtered["Artist"].value_counts().cumsum()
        listen_count = artist_listens_cumulative_df.max() * (artist_filter/100)
        filtered_artists = artist_listens_cumulative_df[artist_listens_cumulative_df < listen_count].index.values
        filtered_df = df_date_filtered[df_date_filtered["Artist"].isin(filtered_artists)]
        artists_fig = px.histogram(filtered_df, x="Artist")
        st.plotly_chart(artists_fig)

    # album
    st.write("### Albums	:minidisc:")
    album_filter = st.selectbox("Top %", [25, 50, 75, 100], index=3, key="album_filter")
    if album_filter == 100:
        album_fig = px.histogram(df_date_filtered, x="Album name")
        st.plotly_chart(album_fig)
    else:
        album_listens_cumulative_df = df_date_filtered["Album name"].value_counts().cumsum()
        listen_count = album_listens_cumulative_df.max() * (album_filter/100)
        filtered_album = album_listens_cumulative_df[album_listens_cumulative_df < listen_count].index.values
        filtered_df = df_date_filtered[df_date_filtered["Album name"].isin(filtered_album)]
        album_fig = px.histogram(filtered_df, x="Album name")
        st.plotly_chart(album_fig)

    # track
    st.write("### Tracks :musical_score:")
    track_filter = st.selectbox("Top %", [25, 50, 75, 100], index=3, key="track_filter")
    if track_filter == 100:
        track_fig = px.histogram(df_date_filtered, x="Song and Artist name")
        st.plotly_chart(track_fig)
    else:
        track_listens_cumulative_df = df_date_filtered["Song and Artist name"].value_counts().cumsum()
        listen_count = track_listens_cumulative_df.max() * (track_filter/100)
        filtered_track = track_listens_cumulative_df[track_listens_cumulative_df < listen_count].index.values
        filtered_df = df_date_filtered[df_date_filtered["Song and Artist name"].isin(filtered_track)]
        track_fig = px.histogram(filtered_df, x="Song and Artist name")
        st.plotly_chart(track_fig)

    # countries
    st.write("### Countries :world_map:")
    st.write("We have the country codes, now we need to convert that to lat long.")
    st.dataframe(df_date_filtered["Country"].unique())

    # listening stats
    st.write("### Time :stopwatch: :hourglass_flowing_sand:")

    # most popular hour of the day
    hours_df = df_date_filtered.groupby(["Hour"])
    songs_per_hour_df = hours_df["Hour"].value_counts().to_frame()
    songs_per_hour_df.reset_index(inplace=True)
    songs_per_hour_fig = px.bar(songs_per_hour_df, x="Hour", y="count", title="Total number of songs played each hour across listening history")
    st.plotly_chart(songs_per_hour_fig)

    # hours per day
    days_df = df_date_filtered.groupby(["Day name"])
    hours_per_day_df = days_df["Milliseconds played"].sum().to_frame()
    hours_per_day_df.reset_index(inplace=True)
    hours_per_day_df["hours"] = hours_per_day_df["Milliseconds played"]/3600000
    hours_per_day_fig = px.bar(hours_per_day_df, x="Day name", y="hours",
                               category_orders={"Day name": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]},
                               title="Time in hours listened per day across entire listening history")
    st.plotly_chart(hours_per_day_fig)

    # monthly listening time
    months_df = df_date_filtered.groupby(["Month number"])
    songs_per_month_df = months_df["Month number"].value_counts().to_frame()
    songs_per_month_df.reset_index(inplace=True)
    songs_per_month_fig = px.bar(songs_per_month_df, x="Month number", y="count", range_x=[1,13], title="Total number of songs played each month across listening history")
    st.plotly_chart(songs_per_month_fig)

    # discovery history
    st.write("### Discovery History :mag:")
    discovery_df = df_date_filtered.sort_values(by="Datetime")
    discovery_df.drop_duplicates(subset=["Song and Artist name"], keep="first", inplace=True)
    discovery_df["type"] = "Discovered"
    discovery_df.drop("Genre", axis=1, inplace=True)
    discovery_fig = px.histogram(discovery_df, x="Datetime", title="Discovery history of songs")
    st.plotly_chart(discovery_fig)

    repeated_df = pd.merge(df_date_filtered, discovery_df, how="outer", indicator=True)
    repeated_df = repeated_df[repeated_df._merge == "left_only"]
    repeated_df["type"] = "Repeated"
    combined_df = pd.concat([discovery_df, repeated_df])
    combined_discovery_fig = px.histogram(combined_df, x="Datetime", color="type", title="Comparison to total songs listened to")
    st.plotly_chart(combined_discovery_fig)
