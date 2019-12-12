package main

import (
	"encoding/json"
	"fmt"
	"os"
	"runtime"
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

func (f Future) GetNext(time int) (a Actor, found bool) {
	if arr, found := f[time]; found && len(arr) > 0 {
		sort.SliceStable(arr, func(i, j int) bool {
			return Priority(arr[i].string) < Priority(arr[j].string)
		})
		a = arr[0].Actor
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




type Actor interface {
	Execute() Op
}
type Op struct {
	duration int
	kind string
}
type Cell struct {
	Actor
	string
}

type Cargo struct {
	Id          int `json:"cargo_id"`
	Destination string `json:"destination"`
	Origin      string `json:"origin"`
}

type Loc struct {
	id    string
	cargo []Cargo
}

type Event struct {
	TransportId string `json:"transport_id"`
	Kind string `json:"kind"`
	Event string `json:"event"`
	Time int `json:"time"`
	Location string `json:"location"`
	Cargo []Cargo `json:"cargo,omitempty"`
	Duration int `json:"duration"`
	Destination string `json:"destination,omitempty"`
}

func (l Loc) getCargo(count int) []Cargo {
	take := l.cargo[:4]
	l.cargo = l.cargo[4:]
	return take
}

var TIME = 0

var (
	FACTORY    = &Loc{id: "FACTORY"}
	A, B, PORT = &Loc{id: "A"}, &Loc{id: "B"}, &Loc{id: "PORT"}
)

type Transport struct {
	id    string
	loc   *Loc
	home  *Loc
	cargo []Cargo
	unlock  chan Op
}

func (t *Transport) log(e *Event) {
	e.TransportId = t.id
	e.Time = TIME
	e.Kind = t.id[:5]
	e.Location = t.loc.id
	e.Cargo=t.cargo
	if data, err := json.Marshal(e); err == nil {
		fmt.Println(string(data))
	}
}

func (t *Transport) Execute() Op{

	op := <- t.unlock
	return op

}

func (t *Transport) sleep(duration int, priority string){


	t.unlock <- Op{duration, priority}
}

func (t *Transport) travel(dest *Loc, eta int) {
	t.log(&Event{Event:"DEPART", Destination:dest.id})
	t.loc = nil
	t.wait <- Op{eta, "arrive"}
	t.loc = dest
	t.log(&Event{Event:"ARRIVE"})
}

func (t *Transport) deliver(dest *Loc, eta int, c []Cargo, load_time int) {
	t.cargo = c
	t.log(&Event{Event:"LOAD", Duration:load_time})
	t.wait <- Op{load_time, "load"}

	t.travel(dest, eta)
	t.log(&Event{Event:"UNLOAD", Duration:load_time})
	t.wait <- Op{load_time, "load"}

	dest.cargo = append(dest.cargo, c...)
	t.cargo = nil

	t.travel(t.home, eta)
}

func (t *Transport) run() {
	for {
		for len(t.home.cargo) == 0 {
			t.wait <- Op{1, "wait"}
		}
		t.wait <- Op{0, "wait"}

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
	runtime.GOMAXPROCS(1)

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
		wait := make(chan Op)
		t.wait = wait
		t.loc = t.home
		future.Schedule(0, Cell{t, "wait"})
		go t.run()
	}

	for len(A.cargo)+len(B.cargo) < len(input) {
		for {
			if a, found := future.GetNext(TIME); found {
				op := a.Execute() // unblock and take next
				fmt.Println("Schedule in ", op.duration)
				future.Schedule(TIME+op.duration, Cell{a, op.kind})
			} else {
				break
			}
		}

		TIME += 1

	}

}
