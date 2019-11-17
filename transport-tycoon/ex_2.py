import json
import sys
from dataclasses import dataclass

INPUT = 'AABABBAB' if len(sys.argv) == 1 else sys.argv[1]
print(f"# Deliver {INPUT}")


@dataclass
class Cargo:
    cargo_id: int
    destination: str
    origin: str


TIME = 0
FACTORY = [Cargo(i, x, 'FACTORY') for i, x in enumerate(INPUT)]
A = []
B = []
PORT = []

WORLD = {'FACTORY': FACTORY, 'PORT': PORT, 'A': A, 'B': B}
PLAN = {
    ('TRUCK', 'FACTORY', 'A'): ('PORT', 1),
    ('TRUCK', 'FACTORY', 'B'): ('B', 5),
    ('TRUCK', 'PORT', None): ('FACTORY', 1),
    ('TRUCK', 'B', None): ('FACTORY', 5),
    ('SHIP', 'PORT', 'A'): ('A', 4),
    ('SHIP', 'A', None): ('PORT', 4),
}


class Transport:
    def __init__(self, id, loc, kind):
        self.id = id
        self.loc = loc
        self.kind = kind
        self.eta = 0
        self.cargo = None

    def log(self, e, **kwargs):
        if self.cargo:
            kwargs['cargo'] = [self.cargo.__dict__]
        e = {'event': e, 'time': TIME, 'transport_id': self.id, 'kind': self.kind, 'location': self.loc, **kwargs}
        print(json.dumps(e))

    def move(self):
        if TIME and self.eta == TIME:
            self.log('ARRIVE')
        if self.eta > TIME:
            return

        place = WORLD[self.loc]
        destination = None
        if self.cargo:
            place.append(self.cargo)
            self.log('UNLOAD')
            self.cargo = None
        else:
            if place:
                self.cargo = place.pop(0)
                destination = self.cargo.destination
                self.log('LOAD')

        plan = (self.kind, self.loc, destination)

        if plan in PLAN:
            destination, eta = PLAN[plan]
            self.log('DEPART', destination=destination)
            self.loc = destination
            self.eta = eta + TIME
        else:
            # print(f'{self.kind} has no plan for {plan}')
            pass


transport = [Transport(2, 'PORT', 'SHIP'), Transport(0, 'FACTORY', 'TRUCK'), Transport(1, 'FACTORY', 'TRUCK'), ]


def cargo_delivered():
    return len(A) + len(B) == len(INPUT)


while not cargo_delivered():
    for t in transport:
        t.move()

    TIME +=1
