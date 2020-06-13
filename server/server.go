package main

import (
	"log"
	"net"
	"os"
)

var Queue *PlayersQueue
var Rooms []*Room

func main() {
	// server address
	udpAddr := &net.UDPAddr{
		IP:   net.ParseIP("127.0.0.1"),
		Port: 8080,
	}

	udpLn, err := net.ListenUDP("udp", udpAddr)

	if err != nil {
		log.Fatalln(err)
		os.Exit(1)
	}

	buf := make([]byte, 1024)
	log.Println("Starting udp server...")

	for {
		n, addr, err := udpLn.ReadFromUDP(buf) // wait here for incoming packets
		if err != nil {
			log.Fatalln(err)
			os.Exit(1)
		}

		go packetHandler(n, addr, buf)
	}
}
