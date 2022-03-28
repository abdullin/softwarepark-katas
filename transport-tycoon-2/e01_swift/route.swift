import Cocoa

class Leg {
    var current: String
    var previous: Leg?
    
    init(_ current: String, _ previous: Leg? = nil){
        self.current = current
        self.previous = previous
    }
}

struct Road {
    var to: String
    var km: Int
}

var graph: [String:[Road]] = [:]

let path = "/Users/rinat/proj/swp-katas/transport-tycoon/s02e01_map.csv"
                
let data = try! String(contentsOfFile: path)
    .trimmingCharacters(in: .whitespacesAndNewlines)

for line in data.components(separatedBy: "\n")[1...]{
    let splits = line.components(separatedBy: ",")
    let a = splits[0], b=splits[1], km = Int(splits[2])!
    graph[a, default: []].append(Road(to: b, km: km))
    graph[b, default: []].append(Road(to: a, km: km))
}

let start = "Steamdrift"
let end = "Leverstorm"
var future: [(time: Int, travel:Leg)] = []
var visited: [String] = []

future.append((time:0, Leg(start, nil)))

while future.count>0 {
    future.sort {$0.time < $1.time}
    let (distance, leg) = future.remove(at: 0)
    let loc = leg.current
    if visited.contains(loc) {
        continue
    }
    
    if loc == end {
        // we arrived. Let's reverse the trip history to print it
        var path = [leg.current]
        var current = leg
        while current.previous != nil {
            current = current.previous!
            path.append(current.current)
        }
        print(path.reversed().joined(separator: ", "))
    }
    visited.append(loc)
    
    for road in graph[loc]!{
        if !visited.contains(road.to){
            let target = distance + road.km
            future.append((target, Leg(road.to, leg)))
        }
    }
}
