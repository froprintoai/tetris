package main

import (
	"bytes"
	"log"
	"net"
	"os"
	"sync"
)

func UDPServer(wg *sync.WaitGroup) {
	udpLn, err := net.ListenUDP("udp", laddrUDP)

	if err != nil {
		log.Fatalln(err)
		os.Exit(1)
	}
	defer udpLn.Close()

	buf := make([]byte, 1024)
	log.Println("Starting udp server...")

	for {
		n, addr, err := udpLn.ReadFromUDP(buf) // wait here for incoming packets
		if err != nil {
			log.Println(err)
			break
		}

		go packetHandler(udpLn, n, addr, buf)
	}
	wg.Done()
}

func packetHandler(conn *net.UDPConn, n int, remoteAddr *net.UDPAddr, buf []byte) {
	if n > 4 {
		magicNumber := buf[0:2]
		if bytes.Equal(magicNumber, []byte("CD")) { // stack info
			roomIndex := int(buf[2])
			roomSide := int(buf[3])   // 0 or 1
			otherSide := 1 - roomSide // 1 or 0

			stack := buf[4:n]
			dest := rooms.RoomSlice[roomIndex].players[otherSide].addrUDP
			contents := append([]byte("XY"), stack...)
			conn.WriteToUDP(contents, dest)
		} else if bytes.Equal(magicNumber, []byte("EF")) { // back to back

		}
	}
}
