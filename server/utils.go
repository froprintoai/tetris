package main

import "net"

type Player struct {
	addr *net.UDPAddr
}

type PlayersQueue struct {
	players []*Player
}

type Room struct {
	player1 *Player
	player2 *Player
}
