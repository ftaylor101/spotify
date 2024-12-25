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
        self.music_activity_df = pd.read_csv(csv_file_path)
        self.music_activity_df = self.music_activity_df[self.COLUMNS]

        self.identifier_df = pd.read_json(identifier_file_path)
        self.library_tracks_df = pd.read_json(library_tracks_file_path)

        # Merge the DataFrames on 'Song Name' and 'Title' columns
        merged_df = pd.merge(self.music_activity_df, self.identifier_df, left_on='Song Name', right_on='Title')
        converted_df = merged_df.astype({'Identifier': int})
        # Merge the DataFrames on 'Identifier' and 'Apple Music Identifier' columns
        self.df = pd.merge(converted_df, self.library_tracks_df, left_on='Identifier', right_on='Apple Music Track Identifier')

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

    clean_df = df.dropna(subset=['IP Latitude', 'IP Longitude'])
    lat_lon_df = clean_df[['IP Latitude', 'IP Longitude']]
    lat_lon_df.rename(columns={'IP Latitude': 'latitude', 'IP Longitude': 'longitude'}, inplace=True)
    st.map(lat_lon_df, latitude="IP Latitude", longitude="IP Longitude")
