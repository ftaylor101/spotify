# Apple Music
There is a lot of information in the Apple Music data.

The files that on first look appear the most interesting are:
* Apple Music - Play History Daily Tracks.csv
* Apple Music Play Activity.csv
* Apple Music - Container Details.csv


### Play History Daily Tracks
Looks like a list of tracks playes each day. Possibly quite useful, has concatenated the artist and song name into a single column. Play Count tally seems useless as the same song appears multiple times with a play count of 1.

### Apple Music Play Activity
This has a lot of information, specifically it looks like each time any song was played. Really annoylingly it does not have the artist name. It has song play time, end reason, platform used, it has city, country and lat/lon so some cool (and worrying) maps can be plotted.It even has the network provider. But it does not have the artist name!!!
* Conainer ID is the album ID, can be matched to Identifier Information.json
* Apple Music Library Albums.json has the album ID and album name, which matches to what is in the Play Activity csv.



## Other useful files
* Apple_Media_Services\Apple_Media_Services\Apple Music Activity\Identifier Information.json
This appears to have the identifiers for artists, albums and songs. This may have to be referred back to when analysing other files. However it doesn't always match up to idenitfiers in Play History Daily Tracks.csv.

* C:\t\Apple_Media_Services\Apple_Media_Services\Apple Music Activity\Apple Music - Top Content.csv
Ranks artists by play time.


### What can we do...
Go to Play Activity.csv, go to column DL and get the song name, album name and container ID. Then go to Identifier Information.json and search for the song name to get the artist identifier, go to Apple Music Library Tracks.json and search for the identifier to get the artist.