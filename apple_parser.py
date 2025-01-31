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

    def __init__(self, csv_file_path: str, identifier_file_path: str, library_tracks_file_path: str):
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

        # Merge the DataFrames on common columns: 'Song Name' and 'Album Name'
        self.df = self.music_activity_df.merge(self.library_tracks_df, on=['Song Name', 'Album Name'], how="inner")

        # Create new columns or rename existing
        self.df["Datetime"] = pd.to_datetime(self.df["Event Start Timestamp"], format='mixed')
        self.df["Day name"] = self.df["Datetime"].dt.day_name()
        self.df["Day number"] = self.df["Datetime"].dt.day
        self.df["Month number"] = self.df["Datetime"].dt.month
        self.df["Year"] = self.df["Datetime"].dt.year
        self.df["Hour"] = self.df["Datetime"].dt.hour
        self.df["Song and Artist name"] = self.df["Song Name"] + " | " + self.df["Artist"]
        self.df["Genre"] = self.df["Genre"].apply(lambda x: [x])
        self.df["Platform"] = self.df["Device OS Name"] + " | " + self.df["Device Type"] + " | " + self.df["Device OS Version"]
        self.df["Milliseconds played"] = self.df["Play Duration Milliseconds"]
        self.df.replace({"End Reason Type": self.END_REASON_DICT}, inplace=True)
        self.df.replace({"Shuffle Play": self.SHUFFLE_DICT}, inplace=True)
        self.df.replace({"IP Country Code": self.COUNTRY_DICT}, inplace=True)
        self.df["Latitude"] = self.df["IP Latitude"]
        self.df["Longitude"] = self.df["IP Longitude"]

        self.df = self.df.rename(columns=self.RENAME_COLUMNS)[self.COLUMNS_FOR_ANALYSIS]

    def get_dataframe(self):
        return self.df


if __name__ == '__main__':
    apple_parser = AppleParser(
        './data/apple/Apple Music Play Activity.csv',
        './data/apple/Identifier Information.json',
        './data/apple/Apple Music Library Tracks.json'
    )
    df = apple_parser.get_dataframe()
    st.write(df.head(50))

    clean_df = df.dropna(subset=['Latitude', 'Longitude'])
    st.map(clean_df, latitude="Latitude", longitude="Longitude")
