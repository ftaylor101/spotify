import json
import pandas as pd
import requests
import streamlit as st

from os import environ
from dotenv import load_dotenv

from collections import defaultdict


class SpotifyParser:
    REQUIRED_COLUMNS = [
        'ts',
        'platform',
        'ms_played',
        'conn_country',
        'master_metadata_track_name',
        'master_metadata_album_artist_name',
        'master_metadata_album_album_name',
        'spotify_track_uri',
        'reason_end',
        'shuffle'
    ]

    END_REASON_DICT = {
        "logout": "logout",
        "trackerror": "track_error",
        "switched-to-video": "switched-to-video",
        "trackdone": "track_done",
        "unknown": "unknown",
        "endplay": "pause",
        "unexpected-exit": "suspended",
        "backbtn": "back_button",
        "fwdbtn": "forward_button",
        "NaN": "unknown",
        "remote": "unknown",
        "unexpected-exit-while-paused": "suspended"
    }

    SHUFFLE_DICT = {
        True: "On",
        False: "Off"
    }

    def __constant_factory(value):
        return lambda: value

    COUNTRY_DICT = defaultdict(__constant_factory("Unknown"))
    COUNTRY_LIST = [
        ("AD",  "Andorra"),
        ("AE",  "United Arab Emirates"),
        ("AF",  "Afghanistan"),
        ("AG",  "Antigua and Barbuda"),
        ("AI",  "Anguilla"),
        ("AL",  "Albania"),
        ("AM",  "Armenia"),
        ("AO",  "Angola"),
        ("AQ",  "Antarctica"),
        ("AR",  "Argentina"),
        ("AS",  "American Samoa"),
        ("AT",  "Austria"),
        ("AU",  "Australia"),
        ("AW",  "Aruba"),
        ("AX",  "Åland Islands"),
        ("AZ",  "Azerbaijan"),
        ("BA",  "Bosnia and Herzegovina"),
        ("BB",  "Barbados"),
        ("BD",  "Bangladesh"),
        ("BE",  "Belgium"),
        ("BF",  "Burkina Faso"),
        ("BG",  "Bulgaria"),
        ("BH",  "Bahrain"),
        ("BI",  "Burundi"),
        ("BJ",  "Benin"),
        ("BL",  "Saint Barthélemy"),
        ("BM",  "Bermuda"),
        ("BN",  "Brunei Darussalam"),
        ("BO",  "Bolivia, Plurinational State of"),
        ("BQ",  "Bonaire, Sint Eustatius and Saba"),
        ("BR",  "Brazil"),
        ("BS",  "Bahamas"),
        ("BT",  "Bhutan"),
        ("BV",  "Bouvet Island"),
        ("BW",  "Botswana"),
        ("BY",  "Belarus"),
        ("BZ",  "Belize"),
        ("CA", "Canada"),
        ("CC", "Cocos (Keeling) Islands"),
        ("CD", "Congo, the Democratic Republic of"),
        ("CF", "Central African Republic"),
        ("CG", "Congo"),
        ("CH", "Switzerland"),
        ("CI", "Côte d'Ivoire"),
        ("CK", "Cook Islands"),
        ("CL", "Chile"),
        ("CM", "Cameroon"),
        ("CN", "China"),
        ("CO", "Colombia"),
        ("CR", "Costa Rica"),
        ("CU", "Cuba"),
        ("CV", "Cabo Verde"),
        ("CW", "Curaçao"),
        ("CX", "Christmas Island"),
        ("CY", "Cyprus"),
        ("CZ", "Czech Republic"),
        ("DE", "Germany"),
        ("DJ", "Djibouti"),
        ("DK", "Denmark"),
        ("DM", "Dominica"),
        ("DO", "Dominican Republic"),
        ("DZ", "Algeria"),
        ("EC", "Ecuador"),
        ("EE", "Estonia"),
        ("EG", "Egypt"),
        ("EH", "Western Sahara"),
        ("ER", "Eritrea"),
        ("ES", "Spain"),
        ("ET", "Ethiopia"),
        ("FI", "Finland"),
        ("FJ", "Fiji"),
        ("FK", "Falkland Islands (Malvinas)"),
        ("FM", "Micronesia, Federated States of"),
        ("FO", "Faroe Islands"),
        ("FR", "France"),
        ("GA", "Gabon"),
        ("GB", "United Kingdom"),
        ("GD", "Grenada"),
        ("GE", "Georgia"),
        ("GF", "French Guiana"),
        ("GG", "Guernsey"),
        ("GH", "Ghana"),
        ("GI", "Gibraltar"),
        ("GL", "Greenland"),
        ("GM", "Gambia"),
        ("GN", "Guinea"),
        ("GP", "Guadeloupe"),
        ("GQ", "Equatorial Guinea"),
        ("GR", "Greece"),
        ("GS", "South Georgia and the South Sandwich Islands"),
        ("GT", "Guatemala"),
        ("GU", "Guam"),
        ("GW", "Guinea-Bissau"),
        ("GY", "Guyana"),
        ("HK", "Hong Kong"),
        ("HM", "Heard Island and McDonalds Islands"),
        ("HN", "Honduras"),
        ("HR", "Croatia"),
        ("HT", "Haiti"),
        ("HU", "Hungary"),
        ("ID", "Indonesia"),
        ("IE", "Ireland"),
        ("IL", "Israel"),
        ("IM", "Isle of Man"),
        ("IN", "India"),
        ("IO", "British Indian Ocean Territory"),
        ("IQ", "Iraq"),
        ("IR", "Iran, Islamic Republic of"),
        ("IS", "Iceland"),
        ("IT", "Italy"),
        ("JE", "Jersey"),
        ("JM", "Jamaica"),
        ("JO", "Jordan"),
        ("JP", "Japan"),
        ("KE", "Kenya"),
        ("KG", "Kyrgyzstan"),
        ("KH", "Cambodia"),
        ("KI", "Kiribati"),
        ("KM", "Comoros"),
        ("KN", "Saint Kitts and Nevis"),
        ("KP", "Korea, Democratic People's Republic of"),
        ("KR", "Korea, Republic of"),
        ("KW", "Kuwait"),
        ("KY", "Cayman Islands"),
        ("KZ", "Kazakhstan"),
        ("LA", "Lao People's Democratic Republic"),
        ("LB", "Lebanon"),
        ("LC", "Saint Lucia"),
        ("LI", "Liechtenstein"),
        ("LK", "Sri Lanka"),
        ("LR", "Liberia"),
        ("LS", "Lesotho"),
        ("LT", "Lithuania"),
        ("LU", "Luxembourg"),
        ("LV", "Latvia"),
        ("LY", "Libya"),
        ("MA", "Morocco"),
        ("MC", "Monaco"),
        ("MD", "Moldova, Republic of"),
        ("ME", "Montenegro"),
        ("MF", "Saint Martin (French part)"),
        ("MG", "Madagascar"),
        ("MH", "Marshall Islands"),
        ("MK", "Macedonia, the former Yugoslav Republic of"),
        ("ML", "Mali"),
        ("MM", "Myanmar"),
        ("MN", "Mongolia"),
        ("MO", "Macao"),
        ("MP", "Northern Mariana Islands"),
        ("MQ", "Martinique"),
        ("MR", "Mauritania"),
        ("MS", "Montserrat"),
        ("MT", "Malta"),
        ("MU", "Mauritius"),
        ("MV", "Maldives"),
        ("MW", "Malawi"),
        ("MX", "Mexico"),
        ("MY", "Malaysia"),
        ("MZ", "Mozambique"),
        ("NA", "Namibia"),
        ("NC", "New Caledonia"),
        ("NE", "Niger"),
        ("NF", "Norfolk Island"),
        ("NG", "Nigeria"),
        ("NI", "Nicaragua"),
        ("NL", "Netherlands"),
        ("NO", "Norway"),
        ("NP", "Nepal"),
        ("NR", "Nauru"),
        ("NU", "Niue"),
        ("NZ", "New Zealand"),
        ("OM", "Oman"),
        ("PA", "Panama"),
        ("PE", "Peru"),
        ("PF", "French Polynesia"),
        ("PG", "Papua New Guinea"),
        ("PH", "Philippines"),
        ("PK", "Pakistan"),
        ("PL", "Poland"),
        ("PM", "Saint Pierre and Miquelon"),
        ("PN", "Pitcairn"),
        ("PR", "Puerto Rico"),
        ("PS", "Palestine, State of"),
        ("PT", "Portugal"),
        ("PW", "Palau"),
        ("PY", "Paraguay"),
        ("QA", "Qatar"),
        ("RE", "Réunion"),
        ("RO", "Romania"),
        ("RS", "Serbia"),
        ("RU", "Russian Federation"),
        ("RW", "Rwanda"),
        ("SA", "Saudi Arabia"),
        ("SB", "Solomon Islands"),
        ("SC", "Seychelles"),
        ("SD", "Sudan"),
        ("SE", "Sweden"),
        ("SG", "Singapore"),
        ("SH", "Saint Helena, Ascension and Tristan da Cunha"),
        ("SI", "Slovenia"),
        ("SJ", "Svalbard and Jan Mayen"),
        ("SK", "Slovakia"),
        ("SL", "Sierra Leone"),
        ("SM", "San Marino"),
        ("SN", "Senegal"),
        ("SO", "Somalia"),
        ("SR", "Suriname"),
        ("SS", "South Sudan"),
        ("ST", "Sao Tome and Principe"),
        ("SV", "El Salvador"),
        ("SX", "Sint Maarten (Dutch part)"),
        ("SY", "Syrian Arab Republic"),
        ("SZ", "Swaziland"),
        ("TC", "Turks and Caicos Islands"),
        ("TD", "Chad"),
        ("TF", "French Southern Territories"),
        ("TG", "Togo"),
        ("TH", "Thailand"),
        ("TJ", "Tajikistan"),
        ("TK", "Tokelau"),
        ("TL", "Timor-Leste"),
        ("TM", "Turkmenistan"),
        ("TN", "Tunisia"),
        ("TO", "Tonga"),
        ("TR", "Turkey"),
        ("TT", "Trinidad and Tobago"),
        ("TV", "Tuvalu"),
        ("TW", "Taiwan, Province of China"),
        ("TZ", "Tanzania, United Republic of"),
        ("UA", "Ukraine"),
        ("UG", "Uganda"),
        ("UM", "United States Minor Outlying Islands"),
        ("US", "United States"),
        ("UY", "Uruguay"),
        ("UZ", "Uzbekistan"),
        ("VA", "Holy See"),
        ("VC", "Saint Vincent and the Grenadines"),
        ("VE", "Venezuela, Bolivarian Republic of"),
        ("VG", "Virgin Islands, British"),
        ("VI", "Virgin Islands, U.S."),
        ("VN", "Viet Nam"),
        ("VU", "Vanuatu"),
        ("WF", "Wallis and Futuna"),
        ("WS", "Samoa"),
        ("XK", "Kosovo"),
        ("YE", "Yemen"),
        ("YT", "Mayotte"),
        ("ZA", "South Africa"),
        ("ZM", "Zambia"),
        ("ZW", "Zimbabwe")
    ]

    RENAME_COLUMNS = {
        "master_metadata_album_artist_name": "Artist",
        "master_metadata_album_album_name": "Album name",
        "master_metadata_track_name": "Song name",
        "ms_played": "Milliseconds played",
        "platform": "Platform",
        "reason_end": "End reason",
        "shuffle": "Shuffle",
        "conn_country": "Country"
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

    def __init__(self, json_file_path: str):
        # Populate the country dictionary
        for k, v in self.COUNTRY_LIST:
            self.COUNTRY_DICT[k] = v

        self.df = pd.read_json(json_file_path)
        self.df = self.df[self.REQUIRED_COLUMNS]
        self.df.dropna(subset=["master_metadata_track_name"], inplace=True)

        self.df["Datetime"] = pd.to_datetime(self.df["ts"], format="%Y-%m-%dT%H:%M:%SZ")
        self.df["Day name"] = self.df["Datetime"].dt.day_name()
        self.df["Day number"] = self.df["Datetime"].dt.day
        self.df["Month number"] = self.df["Datetime"].dt.month
        self.df["Year"] = self.df["Datetime"].dt.year
        self.df["Hour"] = self.df["Datetime"].dt.hour

        self.df = self.df.rename(columns=self.RENAME_COLUMNS)
        self.df["Song and Artist name"] = self.df["Song name"] + " | " + self.df["Artist"]

        self.df.replace({"End reason": self.END_REASON_DICT}, inplace=True)
        self.df.replace({"Shuffle": self.SHUFFLE_DICT}, inplace=True)
        self.df.replace({"Country": self.COUNTRY_DICT}, inplace=True)
        self.df["Latitude"] = float("nan")
        self.df["Longitude"] = float("nan")

        load_dotenv()
        self.last_fm_key = environ["LAST_FM_API_KEY"]
        self.song_dict = {}
        self.df["Genre"] = self.df.apply(self.get_track_genre, axis=1)

        self.df = self.df[self.COLUMNS_FOR_ANALYSIS]

    def get_dataframe(self):
        return self.df

    def get_track_genre(self, row):
        if row["Song and Artist name"] in self.song_dict:
            genres = self.song_dict[row["Song and Artist name"]]
            print(genres)
        else:
            headers = {"user-agent": "Music Analyser"}
            payload = {
                "api_key": self.last_fm_key,
                "method": "track.getInfo",
                "format": "json",
                "artist": row["Artist"],
                "track": row["Song name"]
            }
            r = requests.get('https://ws.audioscrobbler.com/2.0/', headers=headers, params=payload)
            try:
                response = r.json()['track']['toptags']['tag']
            except (KeyError, json.JSONDecodeError):
                response = []
            genres = []
            for g in response:
                genres.append(g['name'])
            self.song_dict[row["Song and Artist name"]] = genres
        return genres


if __name__ == '__main__':
    spotify_parser = SpotifyParser('./data/Streaming_History_Audio_2024_4.json')
    df = spotify_parser.get_dataframe()
    st.write(df.head(50))
