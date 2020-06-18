package main

import (
	"log"
	"net"
	"sync"
	"time"
)

// sweeper is expected to be run as a goroutine
// Every 10 seconds, sweeper checks any room stored in rooms,
// 		where either player hasn't been online (sent UDP packet) for more than 5 seconds
// If sweeper finds either one of two players has been offline,
// 		it notifies the other online player of his victory via TCP and deletes the room
// If sweeper finds both of two players has been offline, it just deletes the room by assigning nil
func sweeper(wg *sync.WaitGroup) {
	for {
		time.Sleep(time.Second * 10)
		for i := 0; i < maxRooms; i++ {
			rooms.LockSlice[i] <- 1 // lock
			if rooms.RoomSlice[i] != nil {
				currentTime := time.Now()
				b0 := currentTime.After(rooms.RoomSlice[i].lastAccess[0].Add(time.Second * 5))
				b1 := currentTime.After(rooms.RoomSlice[i].lastAccess[1].Add(time.Second * 5))

				if b0 && b1 { // both players have been offline for more than 5 seconds
					rooms.RoomSlice[i] = nil
				} else if b0 {
					// send "You Won" message to the opponent player
					dest := rooms.RoomSlice[i].players[1].addrTCP
					conn, err := net.DialTCP("tcp", laddrTCP, dest)
					if err != nil {
						log.Println("Error in sweeper : failed to notify winner :", err)
					} else {
						defer conn.Close()
						_, err = conn.Write([]byte("VI")) // "VI"CTORY
						if err != nil {
							log.Println("Error in sweeper : failed to notify winner :", err)
						}
					}
					rooms.RoomSlice[i] = nil
				} else if b1 {
					// send "You Won" message to the opponent player
					dest := rooms.RoomSlice[i].players[0].addrTCP
					conn, err := net.DialTCP("tcp", laddrTCP, dest)
					if err != nil {
						log.Println("Error in sweeper : failed to notify winner :", err)
					} else {
						defer conn.Close()
						_, err = conn.Write([]byte("VI")) // "VI"CTORY
						if err != nil {
							log.Println("Error in sweeper : failed to notify winner :", err)
						}
					}
					rooms.RoomSlice[i] = nil
				}
			}
			<-rooms.LockSlice[i] // unlock
		}
	}

	wg.Done()
}
