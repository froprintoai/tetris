package main

import (
	"bytes"
	"log"
	"net"
	"os"
	"strconv"
	"sync"
)

func TCPServer(wg *sync.WaitGroup) {
	playerQueue := make(chan *Player, 64)

	listener, err := net.ListenTCP("tcp", laddrTCP)
	if err != nil {
		log.Println("Error in starting server : ", err)
		os.Exit(1)
	}

	log.Println("Starting TCP Server...")

	go consume(playerQueue)

	for {
		conn, err := listener.AcceptTCP()
		if err != nil {
			log.Println("error in TCPServer : ", err)
			continue
		}
		// initialize a element of tracker
		raddrString := conn.RemoteAddr().String()
		tracker[raddrString] = make(chan int, 2)
		go handleTCPConnection(conn, playerQueue)
	}

	wg.Done()
}

func handleTCPConnection(conn *net.TCPConn, q chan<- *Player) {
	defer conn.Close()

	raddr := conn.RemoteAddr()

	buf := make([]byte, 1024)
	n, err := conn.Read(buf)
	if err != nil {
		// handle error
		log.Println("error in handleTCPConnection : failed to read from conn : ", err)
		delete(tracker, raddr.String())
	} else if n > 3 {
		magicNumber := buf[0:2]
		if bytes.Equal(magicNumber, []byte("AB")) { // initial request
			host, port, err := net.SplitHostPort(raddr.String())
			if err != nil {
				// handle error
				log.Println("error in handleTCPConnection : failed to split address : ", err)
				delete(tracker, raddr.String())
				return
			}
			ip := net.ParseIP(host)
			portNum, err := strconv.Atoi(port)
			if err != nil {
				log.Println("error in handleTCPConnection : failed to convert port : ", err)
				delete(tracker, raddr.String())
				return
			}

			udpPortNum := convToPort(buf[2], buf[3])
			player := &Player{
				addrTCP: &net.TCPAddr{
					IP:   ip,
					Port: portNum,
				},
				addrUDP: &net.UDPAddr{
					IP:   ip,
					Port: udpPortNum,
				},
			}

			q <- player

			index := <-tracker[raddr.String()]
			side := <-tracker[raddr.String()]
			log.Println("side : ", side)

			if index == maxRooms { // couldn't find an available room
				delete(tracker, raddr.String())
				_, err = conn.Write([]byte{byte(index), byte(side)})
				if err != nil {
					log.Println("error in handleTCPConnection : failed to notify failure on finding rooms : ", err)
				}
			} else {
				delete(tracker, raddr.String())
				_, err = conn.Write([]byte{byte(index), byte(side)}) // notify client of the index of rooms
				if err != nil {
					log.Println("error in handleTCPConnection : failed to notify success in finding rooms : ", err)
					rooms.Delete(index)
				}
			}

		}

	} else {
		delete(tracker, raddr.String())
	}

}

func consume(q <-chan *Player) {
	for {
		p1 := <-q
		p2 := <-q
		room := &Room{
			players: [2]*Player{p1, p2},
		}
		index, err := rooms.Insert(room)
		if err != nil {
			// handle error
			log.Println("error from consume: ", err)
			tracker[p1.addrTCP.String()] <- maxRooms
			tracker[p1.addrTCP.String()] <- 2
			tracker[p2.addrTCP.String()] <- maxRooms
			tracker[p2.addrTCP.String()] <- 2
		} else {
			tracker[p1.addrTCP.String()] <- index
			tracker[p1.addrTCP.String()] <- 0
			tracker[p2.addrTCP.String()] <- index
			tracker[p2.addrTCP.String()] <- 1
		}
	}
}

// take two inputs such as 65 and 31, then combine them to create Port Number
// 65(0100 0000) 31(0001 1111) --> 16671(0100 0000 0001 1111)
func convToPort(b1 byte, b2 byte) (port int) {
	return (int(b1) << 8) + int(b2)
}
