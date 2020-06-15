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
	playerQueue := make(chan *Player, 32)

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
			log.Println("error from TCPServer", err)
			break
			// handler error
		}
		// initialize a element of tracker
		raddrString := conn.RemoteAddr().String()
		tracker[raddrString] = make(chan int, 1)
		go handleTCPConnection(conn, playerQueue)
	}

	wg.Done()
}

func handleTCPConnection(conn *net.TCPConn, q chan<- *Player) {
	defer conn.Close()

	buf := make([]byte, 1024)
	n, err := conn.Read(buf)
	if err != nil {
		// handle error
	}

	if n > 2 {
		magicNumber := buf[0:2]
		if bytes.Equal(magicNumber, []byte("AB")) { // initial request
			raddr := conn.RemoteAddr()

			host, port, err := net.SplitHostPort(raddr.String())
			if err != nil {
				// handle error
			}
			ip := net.ParseIP(host)
			portNum, err := strconv.Atoi(port)
			if err != nil {
				// handle error
			}
			player := &Player{
				addrTCP: &net.TCPAddr{
					IP:   ip,
					Port: portNum,
				},
				addrUDP: &net.UDPAddr{
					IP:   ip,
					Port: 0, // unknown yet
				},
			}

			q <- player
			index := <-tracker[raddr.String()]
			_, err = conn.Write([]byte{byte(index)}) // notify client of the index
			if err != nil {
				log.Println("error from handleTCPConnection")
				// handle error
			}
		}

	}

}

func consume(q <-chan *Player) {
	for {
		p1 := <-q
		p2 := <-q
		room := &Room{
			player1: p1,
			player2: p2,
		}
		index, err := rooms.Insert(room)
		if err != nil {
			// handle error
			log.Println(err)
		} else {
			tracker[p1.addrTCP.String()] <- index
			tracker[p2.addrTCP.String()] <- index
		}
	}
}
