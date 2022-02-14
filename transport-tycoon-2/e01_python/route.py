#!/usr/bin/env python3
"""
Usage: route.py FROM TO

This implements Trustbit Transport Kata Episode 2.1 - Find shortest path on map
https://github.com/Softwarepark/exercises/blob/master/transport-tycoon_21.md
"""

import sys
from queue import PriorityQueue as PQ
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class Leg:
    current: str
    previous: "Leg"


@dataclass
class Road:
    destination: str
    km: int


visited = []
future = PQ()
graph = defaultdict(list)  # port to roads

with open("s02e01_map.csv") as f:
    lines = f.readlines()
    for line in lines[1:]:
        a, b, km = line.split(",")
        graph[a].append(Road(b, int(km)))
        graph[b].append(Road(a, int(km)))

_, start, end = sys.argv
future.put((0, Leg(start, None)))

while not future.empty():
    (distance, trip) = future.get()
    location = trip.current
    if location in visited:
        continue

    if location == end:
        path = [trip.current]
        while trip.previous:
            trip = trip.previous
            path.append(trip.current)
        print(",".join(reversed(path)))
        break

    visited.append(location)

    for road in graph[location]:
        if road.destination in visited:
            continue

        distance_at = distance + road.km
        future.put((distance_at, Leg(road.destination, trip)))
