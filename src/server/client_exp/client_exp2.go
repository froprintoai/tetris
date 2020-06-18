package main

import (
	"fmt"
	"log"
	"net"
	"os"
	"time"
)

func main() {
	laddr := &net.TCPAddr{
		IP:   net.ParseIP("127.0.0.1"),
		Port: 38336,
	}
	raddr := &net.TCPAddr{
		IP:   net.ParseIP("127.0.0.1"),
		Port: 8000,
	}
	conn, err := net.DialTCP("tcp", laddr, raddr)
	if err != nil {
		log.Println(err)
		os.Exit(1)
	}
	defer conn.Close()
	sendData := append([]byte("AB"), byte(65))
	sendData = append(sendData, byte(31))
	_, err = conn.Write(sendData)
	if err != nil {
		log.Println(err)
		os.Exit(1)
	}

	buf := make([]byte, 1024)
	_, err = conn.Read(buf)
	if err != nil {
		log.Println("error occured")
		os.Exit(1)
	}
	// room found

	index := int(buf[0])
	roomSide := int(buf[1])

	laddrUDP := &net.UDPAddr{
		IP:   net.ParseIP("127.0.0.1"),
		Port: 16671,
	}
	udpLn, err := net.ListenUDP("udp", laddrUDP)
	if err != nil {
		log.Fatalln("failed to start UDP server : ", err)
	}
	defer udpLn.Close()

	go udpServer(udpLn)
	time.Sleep(time.Second)
	go udpClient(udpLn, index, roomSide)

	time.Sleep(time.Minute)
}

func udpServer(udpLn *net.UDPConn) {

	log.Println("Starting udp server...")

	for {
		buf := make([]byte, 1024)
		n, _, err := udpLn.ReadFromUDP(buf) // wait here for incoming packets
		if err != nil {
			log.Println("Error in UDPServer : Failed to read from client: ", err)
			continue
		}
		fmt.Println(string(buf[:n]))
	}

}

func udpClient(udpLn *net.UDPConn, index int, roomSide int) {
	raddrUDP := &net.UDPAddr{
		IP:   net.ParseIP("127.0.0.1"),
		Port: 8080,
	}
	for {
		data := []byte("CD")
		data = append(data, byte(index), byte(roomSide))
		data = append(data, []byte("FROM_CLIENT1")...)
		udpLn.WriteToUDP(data, raddrUDP)
		time.Sleep(time.Second)
	}
}
