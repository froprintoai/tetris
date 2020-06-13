package main

import (
	"bytes"
	"net"
)

func packetHandler(n int, addr *net.UDPAddr, buf []byte) {
	if n > 2 {
		magicNum := buf[0:2]
		if bytes.Equal(magicNum, []byte("AB")) {
			// notify client at addr that the server receives packets
		} else if bytes.Equal(magicNum, []byte("CD")) {

		}
	}
	//log.printf("reciving data: %s from %s", string(buf[:n]), addr.string())

	//log.printf("sending data..")
	//udpln.writeto([]byte("pong"), addr)
	//log.printf("complete sending data..")
}
