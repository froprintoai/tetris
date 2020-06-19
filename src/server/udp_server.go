package main

import (
	"bytes"
	"log"
	"net"
	"sync"
)

func UDPServer(wg *sync.WaitGroup) {
	udpLn, err := net.ListenUDP("udp", laddrUDP)

	if err != nil {
		log.Fatalln("failed to start UDP server : ", err)
	}
	defer udpLn.Close()

	log.Println("Starting udp server...")

	for {
		buf := make([]byte, 1024)
		n, addr, err := udpLn.ReadFromUDP(buf) // wait here for incoming packets
		if err != nil {
			log.Println("Error in UDPServer : Failed to read from client: ", err)
			continue
		}
		//temp := buf[:n]
		//log.Println("get from ", addr, " message : ", temp)

		go packetHandler(udpLn, n, addr, buf)
	}
	wg.Done()
}

func packetHandler(conn *net.UDPConn, n int, remoteAddr *net.UDPAddr, buf []byte) {
	if n > 4 {
		magicNumber := buf[0:2]
		if bytes.Equal(magicNumber, []byte("CD")) || bytes.Equal(magicNumber, []byte("EF")) {
			roomIndex := int(buf[2])
			roomSide := int(buf[3])                              // 0 or 1
			dest := rooms.OponentUDPAddress(roomIndex, roomSide) //atomic access
			rooms.UpdateAccess(roomIndex, roomSide)              // atomic update
			info := buf[4:n]                                     // stack info
			var suffix []byte
			if bytes.Equal(magicNumber, []byte("CD")) {
				suffix = []byte("XY") // stack
			} else if bytes.Equal(magicNumber, []byte("EF")) {
				log.Println("get fire")
				suffix = []byte("FI") // fire
				log.Println("Sending to ", dest.String())
			}
			if dest != nil {
				contents := append(suffix, info...)
				_, err := conn.WriteToUDP(contents, dest)
				if err != nil {
					log.Println("error in packetHandler : failed to write : ", err)
				}
			}
		}
	}
}
