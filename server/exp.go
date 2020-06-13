package main

import (
	"bytes"
	"fmt"
)

func show(s []byte) {
	fmt.Println("###########")
	for _, x := range s {
		fmt.Println(x)
	}
	fmt.Println(len(s))
	fmt.Println(cap(s))
	fmt.Println("###########")
}

func main() {
	b := []byte("ABCD")
	suf := b[0:2]
	if bytes.Equal(suf, []byte("AB")) {
		fmt.Println("OK")
	}
}
