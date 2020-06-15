package main

import (
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
	wg.Done()

}
