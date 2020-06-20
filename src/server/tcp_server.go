package main

import (
	"bytes"
	"log"
	"net"
	"os"
	"strconv"
	"sync"
	"time"
)

func TCPServer(wg *sync.WaitGroup) {
	listener, err := net.ListenTCP("tcp", laddrTCP)
	if err != nil {
		log.Println("Error in starting server : ", err)
		os.Exit(1)
	}

	log.Println("Starting TCP Server...")

	go consume()

	for {
		conn, err := listener.AcceptTCP()
		if err != nil {
			log.Println("error in TCPServer : ", err)
			continue
		}
		go handleTCPConnection(conn)
	}

	wg.Done()
}

func handleTCPConnection(conn *net.TCPConn) {
	defer conn.Close()

	raddr := conn.RemoteAddr()

	buf := make([]byte, 1024)
	n, err := conn.Read(buf)
	if err != nil {
		// handle error
		log.Println("error in handleTCPConnection : failed to read from conn : ", err)
	} else if n > 3 {
		magicNumber := buf[0:2]
		if bytes.Equal(magicNumber, []byte("AB")) { // initial request

			// initialize a element of tracker
			raddrString := conn.RemoteAddr().String()
			tracker[raddrString] = make(chan int, 2)

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

			locker.Lock()
			playerQueue <- player
			locker.Unlock()

			pending := &Pending{
				Waiting: true,
				Lock:    &sync.Mutex{},
			}
			go timeoutDetector(player, pending)

			index := <-tracker[raddr.String()]
			side := <-tracker[raddr.String()]

			pending.Lock.Lock()
			pending.Waiting = false
			pending.Lock.Unlock()

			log.Println("index: ", index)
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
		} else if bytes.Equal(magicNumber, []byte("XX")) { // Gameover
			// send "You Won" message to the opponent player
			log.Println("receive gameover message from ", raddr.String())
			roomIndex := int(buf[2])
			roomSide := int(buf[3])
			dest := rooms.OponentTCPAddress(roomIndex, roomSide)
			if dest != nil {
				log.Println("connecting to the other player to send you won message to ", dest.String())
				conn, err := net.DialTCP("tcp", nil, dest)
				if err != nil {
					log.Println("Error in handleTCPConnection : failed to notify winner :", err)
				} else {
					defer conn.Close()
					log.Println("sending you won message ... ")
					_, err = conn.Write([]byte("VI")) // "VI"CTORY
					if err != nil {
						log.Println("Error in handleTCPConnection : failed to notify winner :", err)
					}
				}
			}
			// delete room
			rooms.Delete(roomIndex)
		} else if bytes.Equal(magicNumber, []byte("FI")) {
		}

	} else {
	}

}

func consume() {
	for {
		p1 := <-playerQueue
		p2 := <-playerQueue
		log.Println(p1.addrTCP.String())
		log.Println(p2.addrTCP.String())
		//if p1.addrTCP.IP.String() == p2.addrTCP.IP.String() { // this is for released version
		if p1.addrTCP.String() == p2.addrTCP.String() { // develop version
			log.Println("same player detected")
			tracker[p1.addrTCP.String()] <- maxRooms
			tracker[p1.addrTCP.String()] <- 2
			tracker[p2.addrTCP.String()] <- maxRooms
			tracker[p2.addrTCP.String()] <- 2
		} else {
			room := &Room{
				players:    [2]*Player{p1, p2},
				lastAccess: [2]time.Time{serverStart, serverStart},
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
				log.Println("insertion completed successfully")
				tracker[p1.addrTCP.String()] <- index
				tracker[p1.addrTCP.String()] <- 0
				tracker[p2.addrTCP.String()] <- index
				tracker[p2.addrTCP.String()] <- 1
			}

		}
	}
}

// take two inputs such as 65 and 31, then combine them to create Port Number
// 65(0100 0000) 31(0001 1111) --> 16671(0100 0000 0001 1111)
func convToPort(b1 byte, b2 byte) (port int) {
	return (int(b1) << 8) + int(b2)
}

func timeoutDetector(player *Player, pending *Pending) {
	time.Sleep(time.Second * 8)
	locker.Lock()
	pending.Lock.Lock()
	if pending.Waiting {
		playerQueue <- player
	}
	pending.Lock.Unlock()
	locker.Unlock()
}
