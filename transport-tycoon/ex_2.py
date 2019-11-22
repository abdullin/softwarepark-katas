import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from typing import List

FUTURE = defaultdict(list)
TIME = 0
INPUT = 'AABABBAB' if len(sys.argv) == 1 else sys.argv[1]


@dataclass
class Cargo:
    cargo_id: int
    destination: str
    origin: str


@dataclass
class Loc:
    id: str
    cargo: List[Cargo]

    def get_cargo(self, n: int):
        load = self.cargo[:n]
        del self.cargo[:n]
        return load


FACTORY = Loc("FACTORY", [Cargo(i, x, 'FACTORY') for i, x in enumerate(INPUT)])
A, B, PORT = Loc("A", []), Loc("B", []), Loc("PORT", [])


class Transport:
    def __init__(self, id: str, loc: Loc):
        self.id = id
        self.loc = loc
        self.home = loc
        self.cargo = []

    def log(self, e, **kwargs):
        kwargs['cargo'] = [x.__dict__ for x in self.cargo]
        e = {'event': e, 'time': TIME, 'transport_id': self.id, 'kind': self.id[:5], 'location': self.loc.id, **kwargs}
        print(json.dumps(e))

    def travel(self, destination: Loc, eta: int):
        self.log("DEPART", destination=destination.id)
        self.loc = None
        yield eta, 'arrive'
        self.loc = destination
        self.log("ARRIVE")

    def deliver_cargo(self, destination: Loc, eta, cargo: List[Cargo], load_time: int):
        self.cargo = cargo
        self.log("LOAD", duration=load_time)
        yield load_time, 'load'

        for x in self.travel(destination, eta):
            yield x

        self.log("UNLOAD", duration=load_time)
        yield load_time, 'unload'
        self.loc.cargo.extend(self.cargo)
        self.cargo = []

        for x in self.travel(self.home, eta):
            yield x

    def run(self):
        while True:
            while not self.home.cargo:
                yield 1, 'wait'  # wait for the cargo
            yield 0, 'wait'  # let the others finish deliveries

            if self.home == PORT:
                plan = self.deliver_cargo(A, 6, self.home.get_cargo(4), 1)
            else:
                cargo = self.loc.get_cargo(1)
                if cargo[0].destination == A.id:
                    plan = self.deliver_cargo(PORT, 1, cargo, 0)
                else:
                    plan = self.deliver_cargo(B, 5, cargo, 0)
            for p in plan:
                yield p


PRIORITY = {'arrive': 0, 'unload': 1, 'load': 10, 'wait': 10}

for t in [Transport('TRUCK1', FACTORY), Transport('TRUCK2', FACTORY), Transport('SHIP', PORT)]:
    FUTURE[0].append((t.run(), 'wait'))  # start all transports right now

while len(A.cargo) + len(B.cargo) < len(INPUT):             # while cargo not delivered
    while FUTURE[TIME]:                                     # while the current time has scheduled actors
        FUTURE[TIME].sort(key=lambda x: PRIORITY[x[1]])     # sort actions according to the priority
        actor, _ = FUTURE[TIME].pop(0)                      # get the next actor scheduled to run now
        interval, priority = next(actor)                    # execute actor till it yields
        FUTURE[TIME + interval].append((actor, priority))   # send actor into the future as it asked
    TIME += 1

print(f"# Deliver {INPUT} in {TIME-1}")
