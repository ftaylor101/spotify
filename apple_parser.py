import json
import pandas as pd
import streamlit as st


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
        'Song Name',
        'Start Position In Milliseconds',
        'UTC Offset In Seconds'
    ]

    def __init__(self, csv_file_path: str, identifier_file_path: str, library_tracks_file_path: str):
        self.df = pd.read_csv(csv_file_path)
        self.df = self.df[self.COLUMNS]

        self.identifier = json.load(open(identifier_file_path))
        self.library_tracks = json.load(open(library_tracks_file_path))

    def get_dataframe(self):
        return self.df


if __name__ == '__main__':
    apple_parser = AppleParser(
        'data\\apple\\Apple Music Library Tracks.json',
        'data\\apple\\Identifier Information.json',
        'data\\apple\\Apple Music Library Tracks.json'
    )
    df = apple_parser.get_dataframe()
    st.write(df.head())
