package main

import (
	"log"
	"net"
	"os"
	"sync"
	"time"
)

func main() {
	var wg sync.WaitGroup
	wg.Add(8)
	for i := 0; i < 8; i++ {
		go clientRequest(&wg, 38336+4*i)
		time.Sleep(time.Second)
	}

	wg.Wait()
}

func clientRequest(wg *sync.WaitGroup, port int) {
	//conn, err := net.Dial("tcp", "127.0.0.1:8000")
	laddr := &net.TCPAddr{
		IP:   net.ParseIP("127.0.0.1"),
		Port: port,
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
	conn.Write([]byte("ABCD"))

	buf := make([]byte, 1024)
	_, err = conn.Read(buf)
	if err != nil {
		log.Println("error occured")
		// handle error
	} else {
		log.Println(buf)
	}

	wg.Done()
}
