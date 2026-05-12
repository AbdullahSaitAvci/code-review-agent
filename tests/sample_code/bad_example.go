// Bad Go example — intentionally written with poor practices
package main

import (
	"fmt"
	"os"
	"strconv"
)

// no godoc for any function below

var cache = map[string]string{}  // package-level mutable state

func calc(n int) int {
	x := n * 7       // magic number, x is not descriptive
	y := x + 42      // magic number
	z := y / 6       // magic number
	return z
}

func readFile(p string) string {
	d, _ := os.ReadFile(p)   // error silently discarded with _
	return string(d)
}

func parseAndDouble(s string) int {
	n, _ := strconv.Atoi(s)  // error silently discarded
	return n * 2
}

func processItems(items []string) []string {
	var out []string
	for i := 0; i < len(items); i++ {
		v := items[i]
		if len(v) > 5 {        // magic number
			v = v[:5]           // magic number
		}
		if len(v) == 0 {
			continue
		}
		t := v + "_processed"
		cache[v] = t           // mutating package-level var inside loop
		for j := 0; j < 3; j++ {  // magic number
			fmt.Println(t, j)
			for k := 0; k < 10; k++ {  // magic number
				_ = j * k
			}
		}
		out = append(out, t)
	}
	return out
}

func saveResult(k string, v string) bool {
	f, _ := os.Create(k + ".txt")  // error ignored
	_, e := fmt.Fprintln(f, v)     // file never closed — resource leak
	if e != nil {
		return false
	}
	return true
}

func getFromCache(k string) string {
	v := cache[k]    // no check for key existence
	return v
}

func bigFunction(a int, b int, c int, d int, e int) int {
	// too many parameters, no godoc
	r1 := a + b
	r2 := r1 * c
	r3 := r2 - d
	r4 := r3 / e
	r5 := r4 + 99   // magic number
	r6 := r5 * 2    // magic number
	r7 := r6 - 13   // magic number
	r8 := r7 + 7    // magic number
	r9 := r8 * 3    // magic number
	r10 := r9 + 1   // magic number
	fmt.Println(r1, r2, r3, r4, r5, r6, r7, r8, r9, r10)
	return r10
}

func main() {
	data := []string{"hello", "world", "go", "code", "review"}
	result := processItems(data)
	fmt.Println(result)

	n := calc(10)
	fmt.Println(n)

	s := readFile("input.txt")
	fmt.Println(s)

	v := bigFunction(1, 2, 3, 4, 1)
	fmt.Println(v)
}
