package main

import (
	"net"
	"time"
)

type Player struct {
	addrTCP *net.TCPAddr
	addrUDP *net.UDPAddr
}

func NewPlayer(ip *net.IP) *Player {
	return &Player{
		addrTCP: &net.TCPAddr{
			IP:   *ip,
			Port: 8000,
		},
		addrUDP: &net.UDPAddr{
			IP:   *ip,
			Port: 8080,
		},
	}
}

type Room struct {
	players    [2]*Player
	lastAccess [2]time.Time
}

type Rooms struct {
	LockSlice  []chan int
	RoomSlice  []*Room
	LockOffset chan int
	Offset     int
}

type RoomFullError struct {
	Message string
}

func (e *RoomFullError) Error() string {
	return e.Message
}

func (rs *Rooms) Insert(r *Room) (index int, err error) {
	rs.LockOffset <- 1 // lock offset
	currentIndex := rs.Offset
	<-rs.LockOffset // unlock offset
	counter := 0    // counts loop
	for counter < 2 {
		rs.LockSlice[currentIndex] <- 1        // lock
		if rs.RoomSlice[currentIndex] == nil { // empty
			rs.RoomSlice[currentIndex] = r
			rs.LockOffset <- 1 // lock offset
			rs.Offset = currentIndex + 1
			<-rs.LockOffset              // unlock offset
			<-rs.LockSlice[currentIndex] // unlock

			index = currentIndex
			err = nil
			break
		}

		<-rs.LockSlice[currentIndex] // unlock
		currentIndex = currentIndex + 1
		if currentIndex > maxRooms {
			counter++
			currentIndex %= maxRooms
		}
	}
	if counter >= 2 {
		index = 0
		err = &RoomFullError{
			Message: "Rooms Full",
		}
	}
	return
}

func (rs *Rooms) Delete(index int) {
	rs.LockSlice[index] <- 1 // lock
	rs.RoomSlice[index] = nil
	<-rs.LockSlice[index] // unlock
}

// atomic access
func (rs *Rooms) OponentUDPAddress(index int, side int) (addr *net.UDPAddr) {
	otherSide := 1 - side // 1 or 0
	rooms.LockSlice[index] <- 1
	if rooms.RoomSlice[index] != nil {
		addr = rooms.RoomSlice[index].players[otherSide].addrUDP
	} else {
		addr = nil
	}
	<-rooms.LockSlice[index]
	return addr
}

// atomic access
func (rs *Rooms) OponentTCPAddress(index int, side int) (addr *net.TCPAddr) {
	otherSide := 1 - side // 1 or 0
	rooms.LockSlice[index] <- 1
	if rooms.RoomSlice[index] != nil {
		addr = rooms.RoomSlice[index].players[otherSide].addrTCP
	} else {
		addr = nil
	}
	<-rooms.LockSlice[index]
	return addr
}

// atomic access
func (rs *Rooms) UpdateAccess(index int, side int) {
	rooms.LockSlice[index] <- 1
	if rooms.RoomSlice[index] != nil {
		rooms.RoomSlice[index].lastAccess[side] = time.Now()
	}
	<-rooms.LockSlice[index]
}
