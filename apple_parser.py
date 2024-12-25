import pandas as pd


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
    
    def __init__(self, file_path):
        self.df = pd.read_csv(file_path)
        self.df = self.df[self.COLUMNS]

    def get_dataframe(self):
        return self.df
