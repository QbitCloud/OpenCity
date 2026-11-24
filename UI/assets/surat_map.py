"""Draw the Surat map shown on the Home page, in the dashboard's colours.

Run from the repo root: .venv/bin/python UI/assets/surat_map.py
Map data © OpenStreetMap contributors (ODbL), so the page credits OpenStreetMap under the map.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import requests
from matplotlib import patheffects
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.colors import to_rgb

OUTPUT = Path(__file__).with_name("surat_map.png")
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Area fetched (south, west, north, east) and the part shown: its centre and height in degrees
BBOX = (21.06, 72.55, 21.33, 73.07)
CENTRE = (21.205, 72.81)
HEIGHT = 0.14
ASPECT = 3

# Dashboard theme: page background, roads, the Tapi and the yellow used for scores
BACKGROUND = "#0e1117"
ROAD = "#629de3"
WATER = "#629de3"
ACCENT = "#e5b45e"

# Road opacity and line width, from side streets to highways
ROAD_STYLES = {"minor": (0.2, 0.25), "medium": (0.4, 0.45), "major": (0.7, 0.8)}

QUERY = """
[out:json][timeout:180];
(
  way["highway"~"^(motorway|trunk|primary|secondary|tertiary|unclassified|residential)"]({bbox});
  way["waterway"~"^(river|canal|stream)$"]({bbox});
  way["natural"="water"]({bbox});
  relation["natural"="water"]({bbox});
);
out geom;
"""


# Roads, rivers and lakes around Surat from OpenStreetMap
def fetch():
    query = QUERY.format(bbox=",".join(str(value) for value in BBOX))
    # Overpass refuses requests' default client name, so send a plain one
    headers = {"User-Agent": "city-map-script/1.0"}
    response = requests.post(OVERPASS_URL, data={"data": query}, headers=headers, timeout=300)
    response.raise_for_status()
    return response.json()["elements"]


def road_class(highway):
    highway = highway.replace("_link", "")
    if highway in ("motorway", "trunk", "primary"):
        return "major"
    if highway in ("secondary", "tertiary"):
        return "medium"
    return "minor"


# A lake or river drawn as a relation comes in pieces: join them end to end into closed outlines
def join_rings(pieces):
    rings = []
    while pieces:
        ring = pieces.pop(0)
        while ring[0] != ring[-1]:
            for index, piece in enumerate(pieces):
                if piece[0] == ring[-1]:
                    ring += pieces.pop(index)[1:]
                    break
                if piece[-1] == ring[-1]:
                    ring += pieces.pop(index)[::-1][1:]
                    break
            else:
                break  # cut off at the edge of the fetched area
        rings.append(ring)
    return rings


def draw(elements):
    # Squeeze longitude so the map is not stretched sideways
    scale = np.cos(np.radians(CENTRE[0]))

    def points(geometry):
        return [(point["lon"] * scale, point["lat"]) for point in geometry]

    roads = {"minor": [], "medium": [], "major": []}
    water_lines, water_areas = [], []

    for element in elements:
        tags = element.get("tags", {})
        if element["type"] == "relation":
            pieces = [points(member["geometry"]) for member in element["members"] if member["role"] == "outer"]
            water_areas += join_rings(pieces)
        elif "highway" in tags:
            roads[road_class(tags["highway"])].append(points(element["geometry"]))
        elif "waterway" in tags:
            water_lines.append(points(element["geometry"]))
        else:
            water_areas.append(points(element["geometry"]))

    figure = plt.figure(figsize=(4 * ASPECT, 4), facecolor=BACKGROUND)
    axis = figure.add_axes((0, 0, 1, 1))
    axis.set_facecolor(BACKGROUND)
    # A soft glow around the Tapi and the lakes, then the water itself
    axis.add_collection(PolyCollection(water_areas, facecolors="none", edgecolors=WATER, linewidths=4, alpha=0.15))
    axis.add_collection(PolyCollection(water_areas, facecolors=WATER, edgecolors=WATER, linewidths=0.3))
    axis.add_collection(LineCollection(water_lines, colors=WATER, linewidths=0.6))
    for kind, (alpha, width) in ROAD_STYLES.items():
        axis.add_collection(LineCollection(roads[kind], colors=ROAD, alpha=alpha, linewidths=width))

    centre_x = CENTRE[1] * scale
    axis.set_xlim(centre_x - HEIGHT * ASPECT / 2, centre_x + HEIGHT * ASPECT / 2)
    axis.set_ylim(CENTRE[0] - HEIGHT / 2, CENTRE[0] + HEIGHT / 2)
    axis.axis("off")

    # Fade the map into the page background towards the edges
    rows, columns = np.linspace(0, 1, 200), np.linspace(0, 1, int(200 * ASPECT))
    edge = np.minimum.outer(np.minimum(rows, 1 - rows), np.minimum(columns, 1 - columns) * ASPECT)
    fade = np.zeros((len(rows), len(columns), 4))
    fade[..., :3] = to_rgb(BACKGROUND)
    fade[..., 3] = 1 - np.clip(edge / 0.2, 0, 1)
    axis.imshow(fade, extent=(*axis.get_xlim(), *axis.get_ylim()), aspect="auto", zorder=3)

    # City name and coordinates in the top-left corner, outlined so roads behind them do not show through
    text = {"transform": axis.transAxes, "zorder": 4, "path_effects": [patheffects.withStroke(linewidth=5, foreground=BACKGROUND)]}
    axis.text(0.03, 0.8, "S U R A T", color="white", fontsize=30, fontweight="bold", fontfamily="Noto Sans", **text)
    axis.text(0.2, 0.8, "સુરત", color="white", fontsize=24, fontfamily="Noto Sans Gujarati", **text)
    axis.text(0.032, 0.71, "21.17° N  ·  72.83° E  ·  on the Tapi", color=ACCENT, fontsize=11, fontfamily="Noto Sans", **text)

    figure.savefig(OUTPUT, dpi=200, facecolor=BACKGROUND)
    plt.close(figure)


if __name__ == "__main__":
    draw(fetch())
    print("Saved", OUTPUT)
