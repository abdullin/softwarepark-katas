#!/usr/bin/env python3
"""
Usage: route.py FROM TO

This implements Trustbit Transport Kata Episode 2.1 - Find shortest path on map
https://github.com/Softwarepark/exercises/blob/master/transport-tycoon_21.md

The file is formatted with black
"""

import sys
from queue import PriorityQueue as PQ
from collections import defaultdict


# this is our map
# key is the current location
# value is a list of (location, Time-to-travel)
MAP = defaultdict(list)  # port to roads

with open("s02e02_map.csv") as f:
    lines = f.readlines()
    for line in lines[1:]:
        loc_a, loc_b, km, speed = line.split(",")
        time_to_travel = float(km) / int(speed)
        MAP[loc_a].append((loc_b, time_to_travel))
        MAP[loc_b].append((loc_a, time_to_travel))

_, start, end = sys.argv

visited = []
# priority queue to track how our truck travels through the milestones
# it will have tuples that contain travel history as a linked list: (CLOCK, location, Parent)
# E.g. travel history with just one milestone where truck started in city 'CITY1' will be (0, "CITY1", None)
# If truck arrived to CITY2 at time 12, then the history will look like:
# (12, "CITY2",
#   (0, "CITY1", None)
# )
# The fun part of that is:
# priority queue sorts by the first tuple element, so any running travels will be properly ordered.
# we can represent multuple travels while reusing objects from the previous travels.
# just add new miletstones and link them to the existing travel graph.

travels = PQ()
travels.put((0, start, None))

while not travels.empty():
    trip = travels.get()
    (clock, location, parent) = trip
    if location in visited:
        continue

    if location == end:
        # we arrived. Let's reverse the trip history to print it
        path = [(clock, location)]
        while parent:
            clock, location, parent = parent
            path.append((clock, location))

        for clock, location in reversed(path):
            print(f"{clock:>5.2f}h {'ARRIVE' if clock else 'DEPART'} {location}")
        break

    visited.append(location)

    for destination, time_to_travel in MAP[location]:
        if destination not in visited:
            # this destination wasn't explored, let's check it out
            arrival_time = clock + time_to_travel
            travels.put((arrival_time, destination, trip))
