import pandas as pd
import streamlit as st

from collections import defaultdict


class AppleParser:
    COLUMNS = [
        'Album Name',
        'Container Album Name',
        'Device OS Name',
        'Device OS Version',
        'Device Type',
        'End Position In Milliseconds',
        'End Reason Type',
        'Event End Timestamp',
        'Event Received Timestamp',
        'Event Start Timestamp',
        'Event Timestamp',
        'Event Type',
        'Feature Name',
        'IP City',
        'IP Country Code',
        'IP Latitude',
        'IP Longitude',
        'IP Network Type',
        'Media Duration In Milliseconds',
        'Media Type',
        'Milliseconds Since Play',
        'Play Duration Milliseconds',
        "Shuffle Play",
        'Song Name',
        'Start Position In Milliseconds',
        'UTC Offset In Seconds'
    ]

    END_REASON_DICT = {
        "EXITED_APPLICATION": "logout",
        "FAILED_TO_LOAD": "track_error",
        "MANUALLY_SELECTED_PLAYBACK_OF_A_DIFF_ITEM": "selected_diff_item",
        "NATURAL_END_OF_TRACK": "track_done",
        "NOT_APPLICABLE": "unknown",
        "OTHER": "uknown",
        "PLAYBACK_MANUALLY_PAUSED": "pause",
        "PLAYBACK_SUSPENDED": "suspended",
        "SCRUB_BEGIN": "scrub_begin",
        "SCRUB_END": "scrub_end",
        "TRACK_SKIPPED_BACKWARDS": "back_button",
        "TRACK_SKIPPED_FORWARDS": "forward_button",
        pd.NA: "unknown"
    }

    SHUFFLE_DICT = {
        "SHUFFLE_ON": "On",
        "SHUFFLE_OFF": "Off",
        "SHUFFLE_UNKNOWN": "Unknown"
    }

    def __constant_factory(value):
        return lambda: value

    COUNTRY_DICT = defaultdict(__constant_factory("Unknown"))
    COUNTRY_LIST = [
        ("GB", "United Kingdom"),
        ("AL", "Albania"),
        ("ES", "Spain"),
        ("IE", "Ireland"),
        ("US", "United States")
    ]

    RENAME_COLUMNS = {
        "Album Name": "Album name",
        "Song Name": "Song name",
        "End Reason Type": "End reason",
        "Shuffle Play": "Shuffle",
        "IP Country Code": "Country"
    }

    COLUMNS_FOR_ANALYSIS = [
        "Datetime",
        "Day name",
        "Day number",
        "Month number",
        "Year",
        "Hour",
        "Artist",
        "Album name",
        "Song name",
        "Song and Artist name",
        "Genre",
        "Platform",
        "Milliseconds played",
        "End reason",
        "Shuffle",
        "Country",
        "Latitude",
        "Longitude"
    ]

    def __init__(self, csv_file_path: str, library_tracks_file_path: str, history_daily_tracks: str):
        # Populate the country dictionary
        for k, v in self.COUNTRY_LIST:
            self.COUNTRY_DICT[k] = v

        # cleaning the music activity data
        self.music_activity_df = pd.read_csv(csv_file_path, low_memory=False)
        self.music_activity_df.dropna(subset=['Album Name'], inplace=True)
        self.music_activity_df.dropna(subset=['Song Name'], inplace=True)
        self.music_activity_df = self.music_activity_df[self.music_activity_df['Media Type'] != 'VIDEO']
        self.music_activity_df = self.music_activity_df[self.music_activity_df['Play Duration Milliseconds'] >= 0]
        self.music_activity_df = self.music_activity_df[self.music_activity_df['Event Type'] != 'LYRIC_DISPLAY']
        self.music_activity_df = self.music_activity_df[self.COLUMNS]
        self.music_activity_df.replace({"Event Start Timestamp": ""}, pd.NA, inplace=True)
        self.music_activity_df.dropna(subset=["Event Start Timestamp"], inplace=True)
        self.music_activity_df.replace({"IP Country Code": pd.NA}, "unknown", inplace=True)

        # load, read and rename two columns in library tracks data
        self.library_tracks_df = pd.read_json(library_tracks_file_path)
        library_rename = {"Title": "Song Name", "Album": "Album Name"}
        self.library_tracks_df.rename(columns=library_rename, inplace=True)
        self.library_tracks_df = self.library_tracks_df.filter(['Artist', 'Song Name', 'Album Name'])
        self.library_tracks_df = self.library_tracks_df.drop_duplicates()

        # load, read and clean daily tracks
        self.daily_tracks_df = pd.read_csv(history_daily_tracks)
        self.daily_tracks_df.dropna(subset=['Track Description'], inplace=True)
        split_columns = self.daily_tracks_df['Track Description'].str.split(' - ', expand=True)
        self.daily_tracks_df['Artist'] = split_columns[0]
        self.daily_tracks_df['Song Name'] = split_columns[1]
        self.daily_tracks_df = self.daily_tracks_df.filter(['Artist', 'Song Name'])
        self.daily_tracks_df = self.daily_tracks_df.drop_duplicates()

        self.artist_dict = defaultdict(list)

        # gather the artist names for all songs
        self.music_activity_df['Artist from non exact matches'] = self.music_activity_df.apply(lambda x: self._non_exact_track_names(x["Song Name"]), axis=1)
        self.music_activity_df['Probable Artist'] = self.music_activity_df.apply(lambda x: self._find_artist_in_library(x["Album Name"], x["Song Name"]), axis=1)
        self.music_activity_df["Artist"] = self.music_activity_df["Probable Artist"].fillna(self.music_activity_df["Artist from non exact matches"])

        # Merge the DataFrames on common columns: 'Song Name' and 'Album Name'
        # self.df = self.music_activity_df.merge(self.library_tracks_df, on=['Song Name', 'Album Name'], how="left")

        print(self.music_activity_df.columns)

        # Create new columns or rename existing
        self.music_activity_df["Datetime"] = pd.to_datetime(self.music_activity_df["Event Start Timestamp"], format='mixed')
        self.music_activity_df["Day name"] = self.music_activity_df["Datetime"].dt.day_name()
        self.music_activity_df["Day number"] = self.music_activity_df["Datetime"].dt.day
        self.music_activity_df["Month number"] = self.music_activity_df["Datetime"].dt.month
        self.music_activity_df["Year"] = self.music_activity_df["Datetime"].dt.year
        self.music_activity_df["Hour"] = self.music_activity_df["Datetime"].dt.hour
        self.music_activity_df["Song and Artist name"] = self.music_activity_df["Song Name"] + " | " + self.music_activity_df["Artist"]
        self.music_activity_df["Genre"] = self.music_activity_df["Genre"].apply(lambda x: [x])
        self.music_activity_df["Platform"] = self.music_activity_df["Device OS Name"] + " | " + self.music_activity_df["Device Type"] + " | " + self.music_activity_df["Device OS Version"]
        self.music_activity_df["Milliseconds played"] = self.music_activity_df["Play Duration Milliseconds"]
        self.music_activity_df.replace({"End Reason Type": self.END_REASON_DICT}, inplace=True)
        self.music_activity_df.replace({"Shuffle Play": self.SHUFFLE_DICT}, inplace=True)
        self.music_activity_df.replace({"IP Country Code": self.COUNTRY_DICT}, inplace=True)
        self.music_activity_df["Latitude"] = self.music_activity_df["IP Latitude"]
        self.music_activity_df["Longitude"] = self.music_activity_df["IP Longitude"]

        self.music_activity_df = self.music_activity_df.rename(columns=self.RENAME_COLUMNS)[self.COLUMNS_FOR_ANALYSIS]

    def _find_artist_in_library(self, album: str, song: str) -> str:
        artist = None
        artists_from_track = list(self.daily_tracks_df[self.daily_tracks_df['Song Name'] == song]["Artist"].unique())
        artists_from_album = list(self.library_tracks_df[self.library_tracks_df['Album Name'] == album]["Artist"].unique())
        artists_from_non_exact_song_match = list(self.daily_tracks_df[self.daily_tracks_df.map(lambda x: song.lower() in x.lower() if isinstance(x, str) else False)["Song Name"]]["Artist"].unique())
        potential_artist = list(set(artists_from_track).intersection(artists_from_album))
        if len(artists_from_track) == 1:
            self.artist_dict[artists_from_track[0]].append(album)
            artist = artists_from_track[0]
        elif len(potential_artist) == 1:
            artist = potential_artist[0]
        elif not artist:
            for a in artists_from_track:
                try:
                    tmp_album_list = self.artist_dict[a]
                    if album in tmp_album_list:
                        artist = a
                        break
                except KeyError:
                    pass
        elif len(artists_from_non_exact_song_match) == 1:
            artist = artists_from_non_exact_song_match[0]
        else:
            artist = "I CANNOT FIND THE ARTIST!!!"
        return artist

    def _non_exact_track_names(self, song: str) -> str:
        artist = pd.NA
        list_of_artists = self.daily_tracks_df[self.daily_tracks_df.map(lambda x: song.lower() in x.lower() if isinstance(x, str) else False)["Song Name"]]["Artist"].to_list()
        if list_of_artists:
            artist = list_of_artists[0]
        return artist

    def get_dataframe(self):
        return self.music_activity_df


if __name__ == '__main__':
    apple_parser = AppleParser(
        './data/apple/Apple Music Play Activity.csv',
        './data/apple/Apple Music Library Tracks.json',
        './data/apple/Apple Music - Play History Daily Tracks.csv'
    )
    df = apple_parser.get_dataframe()
    st.write(df.head(150))
    st.write(df.describe())

    clean_df = df.dropna(subset=['Latitude', 'Longitude'])
    st.map(clean_df, latitude="Latitude", longitude="Longitude")
