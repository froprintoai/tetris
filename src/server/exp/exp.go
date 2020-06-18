package main

import (
	"fmt"
	"time"
)

func main() {
	x := []byte("ABC")
	y := append([]byte("XY"), x...)
	fmt.Println(y)

	z := x[1:]
	fmt.Println(z)
	z[0] = 19
	fmt.Println(z)
	fmt.Println(x)

	fmt.Printf("%#v", string(byte(89)))

	fmt.Println(string(x))
	fmt.Println(time.Now())
}
