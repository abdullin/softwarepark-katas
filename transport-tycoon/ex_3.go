package main

import (
	"encoding/json"
	"fmt"
	"os"
	"sort"
)

func Priority(op string) int {
	switch op {
	case "arrive":
		return 0
	case "load":
		return 1
	default:
		return 10
	}
}

type Future map[int][]Cell

func (f Future) GetNext(time int) (a *Transport, found bool) {
	if arr, found := f[time]; found && len(arr) > 0 {
		sort.SliceStable(arr, func(i, j int) bool {
			return Priority(arr[i].string) < Priority(arr[j].string)
		})
		a = arr[0].Transport
		f[time] = arr[1:]
		return a, true
	}
	return nil, false
}

func (f Future) Schedule(time int, c ...Cell) {
	if arr, found := f[time]; found {
		f[time] = append(arr, c...)
	} else {
		f[time] = c
	}
}

type Op struct {
	duration int
	kind     string
}
type Cell struct {
	*Transport
	string
}

type Cargo struct {
	Id          int    `json:"cargo_id"`
	Destination string `json:"destination"`
	Origin      string `json:"origin"`
}

type Loc struct {
	id    string
	cargo []Cargo
}

type Event struct {
	TransportId string  `json:"transport_id"`
	Kind        string  `json:"kind"`
	Event       string  `json:"event"`
	Time        int     `json:"time"`
	Location    string  `json:"location"`
	Cargo       []Cargo `json:"cargo,omitempty"`
	Duration    int     `json:"duration"`
	Destination string  `json:"destination,omitempty"`
}

func (l *Loc) getCargo(count int) []Cargo {
	avail := len(l.cargo)
	if avail > count {
		avail = count
	}

	take := l.cargo[:avail]
	l.cargo = l.cargo[avail:]

	fmt.Println("# left ", len(l.cargo))
	return take
}

var TIME = 0

var (
	FACTORY    = &Loc{id: "FACTORY"}
	A, B, PORT = &Loc{id: "A"}, &Loc{id: "B"}, &Loc{id: "PORT"}
)

type Transport struct {
	id       string
	loc      *Loc
	home     *Loc
	cargo    []Cargo
	messages chan Op

	window chan bool
}

func (t *Transport) log(e *Event) {
	e.TransportId = t.id
	e.Time = TIME
	e.Kind = t.id[:5]
	e.Location = t.loc.id
	e.Cargo = t.cargo
	if data, err := json.Marshal(e); err == nil {
		fmt.Println(string(data))
	}
}

func (t *Transport) wait(duration int, priority string) {
	t.messages <- Op{duration: duration, kind: priority}
	<-t.window
}

func (t *Transport) Step() Op {
	// tell that it can run
	t.window <- true
	// wait for the response
	return <-t.messages
}

func (t *Transport) travel(dest *Loc, eta int) {
	t.log(&Event{Event: "DEPART", Destination: dest.id})
	t.loc = nil
	t.wait(eta, "arrive")
	t.loc = dest
	t.log(&Event{Event: "ARRIVE"})
}

func (t *Transport) deliver(dest *Loc, eta int, c []Cargo, load_time int) {
	t.cargo = c
	t.log(&Event{Event: "LOAD", Duration: load_time})
	t.wait(load_time, "load")

	t.travel(dest, eta)
	t.log(&Event{Event: "UNLOAD", Duration: load_time})
	t.wait(load_time, "load")

	dest.cargo = append(dest.cargo, c...)
	t.cargo = nil

	t.travel(t.home, eta)
}

func (t *Transport) run() {
	<-t.window

	for {
		for len(t.home.cargo) == 0 {
			t.wait(1, "wait")
		}
		t.wait(0, "wait")

		if t.home == PORT {
			t.deliver(A, 6, t.home.getCargo(4), 1)
		} else {
			c := t.home.getCargo(1)
			if c[0].Destination == A.id {
				t.deliver(PORT, 1, c, 0)
			} else {
				t.deliver(B, 5, c, 0)
			}
		}
	}
}

func main() {
	input := "AABABBAB"
	if len(os.Args) == 2 {
		input = os.Args[1]
	}

	future := make(Future)

	for i, c := range input {
		FACTORY.cargo = append(FACTORY.cargo, Cargo{i, string(c), "FACTORY"})
	}

	ts := []*Transport{{id: "TRUCK1", home: FACTORY}, {id: "TRUCK2", home: FACTORY}, {id: "FERRY", home: PORT}}

	for _, t := range ts {
		t.messages = make(chan Op)
		t.window = make(chan bool)
		t.loc = t.home
		future.Schedule(0, Cell{t, "wait"})

		go t.run()
	}

	for len(A.cargo)+len(B.cargo) < len(input) {
		for {
			if a, found := future.GetNext(TIME); found {

				op := a.Step() // unblock and take next
				// fmt.Println("Schedule in ", op.duration)
				future.Schedule(TIME+op.duration, Cell{a, op.kind})
			} else {
				break
			}
		}

		TIME += 1
	}
}
