import Cocoa

class Leg {
    var time: Double
    var current: String
    var previous: Leg?
    
    init(_ time: Double, _ current: String, _ previous: Leg? = nil){
        self.time = time
        self.current = current
        self.previous = previous
    }
}

struct Road {
    var to: String
    var dur: Double
}

var graph: [String:[Road]] = [:]

let path = "/Users/rinat/proj/swp-katas/transport-tycoon/s02e02_map.csv"
                
let data = try! String(contentsOfFile: path)
    .trimmingCharacters(in: .whitespacesAndNewlines)

for line in data.components(separatedBy: "\n")[1...]{
    let splits = line.components(separatedBy: ",")
    let a = splits[0], b=splits[1]
    let duration = Double(splits[2])!/Double(splits[3])!
    graph[a, default: []].append(Road(to: b, dur: duration))
    graph[b, default: []].append(Road(to: a, dur: duration))
}

let start = "Steamdrift"
let end = "Leverstorm"
var future: [Leg] = []
var visited: [String] = []

future.append(Leg(0, start, nil))

while future.count>0 {
    future.sort {$0.time < $1.time}
    let leg = future.remove(at: 0)
    let loc = leg.current
    if visited.contains(loc) {
        continue
    }
    
    if loc == end {
        // we arrived. Let's reverse the trip history to print it
        var path = [(leg.time, leg.current)]
        var current = leg
        while current.previous != nil {
            current = current.previous!
            path.append((current.time, current.current))
        }
        for (n, (t, loc)) in path.reversed().enumerated() {
            let kind = (n==0 ? "DEPART" : "ARRIVE")
            print(String(format: "% 6.2f", t), kind, loc)
        }
        break
    }
    visited.append(loc)
    
    for road in graph[loc]!{
        if !visited.contains(road.to){
            let target = leg.time + road.dur
            future.append(Leg(target, road.to, leg))
        }
    }
}


