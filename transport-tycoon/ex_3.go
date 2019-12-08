package main

import (
	"fmt"
	"runtime"
	"sort"
)




func Priority(op string) int{
	switch op {
	case "arrive": return 0
	case "load": return 1
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

type Actor chan Op
type Op struct {int;string}
type Cell struct{Actor;string}


type Cargo struct {
	id          int
	destination string
	origin      string
}

type Loc struct {
	id    string
	cargo []Cargo
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
	wait  Actor
}


func (t *Transport) log(e string){
	fmt.Printf("{'transport_id':'%s', %v}\n", t.id, e)

}

func (t *Transport) travel(dest *Loc, eta int){
	t.log("DEPART")
	t.loc = nil
	t.wait <- Op{eta,"arrive"}
	t.loc = dest
	t.log("ARRIVE")
}

func (t *Transport) deliver(dest *Loc, eta int, c []Cargo, load_time int){
	t.cargo = c
	t.log("LOAD")
	t.wait <- Op{load_time,"load"}

	t.travel(dest, eta)
	t.log("UNLOAD")
	t.wait <- Op{load_time,"load"}

	dest.cargo = append(dest.cargo, c...)
	t.cargo = nil

	t.travel(t.home, eta)
}

func (t *Transport) run(){
	for {
		for len(t.home.cargo) == 0 {
			t.wait <- Op{1,"wait"}
		}
		t.wait <- Op{0,"wait"}

		if t.home == PORT{
			t.deliver(A,6, t.home.getCargo(4), 1)
		} else{
			c := t.home.getCargo(1)
			if c[0].destination == A.id{
				t.deliver(PORT, 1, c, 0)
			} else {
				t.deliver(B,5, c, 0)
			}
		}
	}
}

func main() {
	runtime.GOMAXPROCS(1)
	input := "AABABBAB"

	for i, c := range input {
		FACTORY.cargo= append(FACTORY.cargo, Cargo{i, string(c), "FACTORY"})
	}


	future := make(Future)


	transports := []*Transport{ {id: "TRUCK1", home: FACTORY}, {id: "TRUCK2", home: FACTORY}, {id: "SHIP", home: PORT}}

	for _, t := range transports{
		wait := make(chan Op)
		t.wait = wait
		future.Schedule(0,Cell{t.wait, "wait"})
		go t.run()
	}

	for len(A.cargo)+len(B.cargo) < len(input) {
		fmt.Println(TIME)
		for {
			if a, found := future.GetNext(TIME); found {
				op := <-a // unblock and take next
				future.Schedule(TIME+op.int, Cell{a,op.string})
			} else {
				break
			}
		}


		TIME += 1

	}

}
