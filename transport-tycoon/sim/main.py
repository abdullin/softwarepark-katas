import json
from collections import defaultdict
from typing import Dict


class Truck:
    pass

class Cargo:
    def __init__(self, a:str, b:str):
        self.origin=a
        self.dest = b

    def __repr__(self):
        return f"Cargo({self.origin}-{self.dest})"

class Warehouse:
    pass

class Link:
    def __init__(self, type:int, distance:int):
        self.type= type
        self.distance= distance

    def __repr__(self):
        if self.type==ROAD:
            return f'ROAD({self.distance})'
        return f'FERRY({self.distance})'


class Transport:
    def __init__(self, type:int, uid: int):
        self.type = type
        self.uid = uid


    def __repr__(self):
        if self.type == ROAD:
            return f'TRUCK-{self.uid}'
        return f'FERRY-{self.uid}'

class Location:
    def __init__(self):
        self.link = {}
        self.transports = []
        self.cargo = []


    def __repr__(self):
        return f'Location({self.transports}, {self.cargo}, {self.link})'


WORLD = {}


ROAD = 'TRUCK'
FERRY = 'FERRY'

links = {}


navs : Dict[str, Location]= defaultdict(Location)


def link(a:str, b:str, type:int, distance:int):
    l = Link(type, distance)

    navs[a].link[b]=l
    navs[b].link[a]=l

TRANSPORT_UID = 0

def put_transport(loc:str, type:int):
    if not loc in navs:
        raise ValueError("Loc not available")

    global TRANSPORT_UID

    navs[loc].transports.append(Transport(type=type, uid=TRANSPORT_UID))

    TRANSPORT_UID+=1

def put_cargo(a, b:str):
    navs[a].cargo.append(Cargo(a,b))


link('FACTORY', 'PORT', ROAD, 1)
link('FACTORY', 'B', ROAD,5)
link('PORT', 'A', FERRY, 4)

put_transport('FACTORY', ROAD)
put_transport('FACTORY', ROAD)

put_transport('PORT', FERRY)


put_cargo('FACTORY', 'A')
put_cargo('FACTORY', 'B')

def map_to_json():

    result = {}
    map = []
    for i, loc in navs.items():


        cargo = []
        for c in loc.cargo:
            cargo.append({'origin':c.origin, 'dest':c.dest})


        transports = [{'uid':x.uid, 'type':x.type} for x in loc.transports]




        links = []

        for l, prop in loc.link.items():
            links.append({
                'to': l,
                'distance': prop.distance,
                'type': prop.type
            })
        map.append({
            'loc':i,
            'links':links,
            'cargo': cargo,
            'transports': transports,

        })

    return map





print(navs)


print(json.dumps(map_to_json(), indent=True))


