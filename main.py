#! /usr/bin/env python3
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from dataclasses import dataclass
from typing import List
from tabulate import tabulate
from argparse import ArgumentParser

SHOW_CHOICES = ["duration", "artist", "album"]


@dataclass
class Artist:
    name: str


@dataclass
class Track:
    name: str
    artist: str  # artists: List[Artist]
    album: str
    duration: str


class SpotifyStats:
    def __init__(self) -> None:
        load_dotenv()
        self.scope = " ".join(
            (
                "user-library-read",
                "user-top-read",
                "user-follow-read",
                "playlist-read-private",
                "user-read-currently-playing",
            )
        )
        self.client = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=self.scope))

    def get_top_tracks(self, n=5, timeframe="medium_term"):
        response = self.client.current_user_top_tracks(limit=n, time_range=timeframe)
        if response is None:
            return None

        top_tracks = []

        for item in response["items"][:n]:
            track_name = item["name"]
            track_artists = ", ".join([j["name"] for j in item["artists"]])
            track_album = item["album"]["name"]
            track_duration = (
                f"{item['duration_ms']//60000} min {(item['duration_ms']//1000)%60} sec"
            )
            track = Track(track_name, track_artists, track_album, track_duration)

            top_tracks.append(track)

        return top_tracks

    @staticmethod
    def get_track_table(top_tracks: List[Track]):
        table = {"Track": [], "Artist": [], "Album": [], "Duration": []}
        for track in top_tracks:
            table["Track"].append(track.name)
            table["Artist"].append(track.artist)
            table["Album"].append(track.album)
            table["Duration"].append(track.duration)

        return table

    # def get_top_tracks_table(self):
    #     return self.get_track_table(self.get_top_tracks())


def get_parser():
    parser = ArgumentParser(prog="spotistats", description="checks your spotify stats")
    parser.add_argument(
        "--num",
        "-n",
        type=int,
        metavar="N",
        help="shows top N results (max=50)",
        default=5,
    )
    parser.add_argument(
        "--time",
        "-t",
        type=str,
        metavar="TIME",
        choices=["short", "medium", "long"],
        help="time frame to check in",
        default="medium",
    )
    # parser.add_argument(
    #     "--album", "-al", help="display album name", action="store_true"
    # )
    # parser.add_argument(
    #     "--artist", "-art", help="display artist name", action="store_true"
    # )
    # parser.add_argument(
    #     "--duration", "-d", help="display duration of track", action="store_true"
    # )
    parser.add_argument(
        "--show", "-s", type=str, choices=SHOW_CHOICES, nargs="+", default=[]
    )

    return parser


def main():
    args = get_parser().parse_args()

    timeframe = args.time + "_term"

    sp = SpotifyStats()
    resp = sp.get_top_tracks(n=args.num, timeframe=timeframe)

    if resp is None:
        print("error occured :(")
        exit(1)

    table = sp.get_track_table(resp)

    for i in SHOW_CHOICES:
        if i not in args.show:
            table.pop(i.title())

    # if not args.album:
    #     table.pop("Album")
    # if not args.artist:
    #     table.pop("Artist")
    # if not args.duration:
    #     table.pop("Duration")

    print(tabulate(table, headers="keys"))


if __name__ == "__main__":
    main()

"""
1. top artists (-time, -number)
2. top tracks (-time, -number)
3. 
4. listerning time (-time)` 
5. all albums
6. all artists
7. current song
8. liked songs
9. top genres
10. wrapped (-time) - tracks, artists, genres, listerning time
11.
"""
