#!/bin/env python

import json
import pathlib
import re
import time

import click
import yaml


def metadata(folder, collection, year, videos):
    """ Return videos.yaml data. """
    return {
        "folder": folder,
        "default_metadata": {
            "mediatype": "movies",
            "licenseurl": "http://creativecommons.org/licenses/by/3.0/",
            "language": "eng",
            "collection": collection,
            "subject": f"pyconza; pyconza{year}; python",
        },
        "videos": videos,
    }


def video_id(title):
    """ Generate an ID slug from a title. """
    title = title.strip().lower()
    return re.sub("[^a-z0-9]+", "-", title)


def video_creators(descr):
    """ Hackily extract the speakers from the description.

        Multiple creators should be semi-colon separated.
    """
    start = "By: "
    for ll in descr.splitlines():
        if ll.startswith(start):
            creators = [
                c.strip() for c in ll[len(start):].split(" & ")
            ]
            return "; ".join(creators)
    raise ValueError("No creators found in description.")


def video_date(descr):
    """ Hackily extract the date from the description.

        Date format should be YYYY-MM-DD.
    """
    start = "Scheduled start: "
    for ll in descr.splitlines():
        if ll.startswith(start):
            parts = ll[len(start):].strip().split()
            if len(parts) != 2:
                raise ValueError("Unable to parse scheduled start line.")
            date, _ = parts
            try:
                time.strptime(date, "%Y-%m-%d")
            except ValueError as err:
                raise ValueError(
                    "Unable to parse scheduled start date."
                ) from err
            return date
    raise ValueError("No scheduled start found in description.")


def video(filename, info, done=False, upload=True):
    """ Return a video metadata dictionary. """
    video_filename = re.sub(r"\.info\.json$", ".webm", filename)
    descr_filename = re.sub(r"\.info\.json$", ".description", filename)
    descr_path = pathlib.Path(descr_filename)
    if descr_path.exists():
        description = descr_path.read_text()
    else:
        description = info["description"]
    return {
        "filename": video_filename,
        "done": done,
        "upload": upload,
        "identifier": video_id(info["title"]),
        "metadata": {
            "title": info["fulltitle"],
            "creator": video_creators(description),
            "description": description,
            "date": video_date(description),
        },
    }


@click.command()
@click.argument("info_files", type=click.Path(exists=True), nargs=-1)
@click.option("--folder", "-f", default=".")
@click.option("--collection", "-c", default="pyconza")
@click.option("--year", default=2021)
@click.option("--out", "-o", default="-", type=click.File(mode="w"))
def yt_to_yaml(folder, collection, year, out, info_files):
    """ Convert YouTube metadata into Internet Archive upload metadata YAMLs.
    """
    videos = []
    for info_file in info_files:
        with open(info_file) as f:
            info = json.load(f)
        videos.append(video(info_file, info))
    md = metadata(
        folder=folder,
        collection=collection,
        year=year,
        videos=videos,
    )
    yaml.safe_dump(md, stream=out)


if __name__ == "__main__":
    yt_to_yaml()
