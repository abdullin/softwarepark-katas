import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from typing import List

FUTURE = defaultdict(list)
TIME = 0
INPUT = 'AABABBAB' if len(sys.argv) == 1 else sys.argv[1]
print(f"# Deliver {INPUT}")


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
A = Loc("A", [])
B = Loc("B", [])
PORT = Loc("PORT", [])


def cargo_delivered():
    return len(A.cargo) + len(B.cargo) == len(INPUT)


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
        yield eta
        self.loc = destination
        self.log("ARRIVE")

    def deliver_cargo(self, destination: Loc, eta, cargo: List[Cargo], load_time: int):
        self.cargo = cargo
        self.log("LOAD")
        yield load_time

        for x in self.travel(destination, eta):
            yield x

        yield load_time
        self.log("UNLOAD")
        self.loc.cargo.extend(self.cargo)
        self.cargo = []

        for x in self.travel(self.home, eta):
            yield x

    def run(self):
        while True:
            while not self.home.cargo:
                yield 1  # wait for the cargo

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


for t in [Transport('TRUCK1', FACTORY), Transport('TRUCK2', FACTORY), Transport('FERRY', PORT)]:
    FUTURE[0].append(t.run())  # start all transports right now

while not cargo_delivered():
    while FUTURE[TIME]:                         # while the current time has scheduled actors
        actor = FUTURE[TIME].pop(0)             # get the next actor scheduled to run now
        interval = next(actor)                  # execute actor till it yields
        FUTURE[TIME + interval].append(actor)   # send actor into the future as it asked
    TIME += 1
