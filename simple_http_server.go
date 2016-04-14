//usr/bin/env go run "$0" "$@" ; exit

// Using pseudo-shebang, as described in:
// http://golangcookbook.com/chapters/running/shebang/
// https://stackoverflow.com/questions/7707178/whats-the-appropriate-go-shebang-line

// The following code is copied from:
// https://stackoverflow.com/a/13970713/

package main

import (
    "fmt"; "log"; "net/http"
)

func main() {
    fmt.Println("Serving files in the current directory on port 8080")
    http.Handle("/", http.FileServer(http.Dir(".")))
    err := http.ListenAndServe(":8080", nil)
    if err != nil {
        log.Fatal("ListenAndServe: ", err)
    }
}
