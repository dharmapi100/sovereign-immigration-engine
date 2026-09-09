package main

import (
	"crypto/hmac"
	"crypto/sha256"
	"database/sql"
	"encoding/hex"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
	"regexp"
	"sync"
	"time"

	_ "github.com/mattn/go-sqlite3"
)

type AuditEntry struct {
	Timestamp string
	Hash      string
	PII       bool
}

var (
	krnRegex = regexp.MustCompile(`\d{6}-\d{7}`)
	db       *sql.DB
	auditChan = make(chan AuditEntry, 1000)
	mu       sync.Mutex
)

func init() {
	var err error
	db, err = sql.Open("sqlite3", "./sovereign_audit.db")
	if err != nil {
		log.Fatal(err)
	}
	// Run worker for async logging
	go auditWorker()
}

func auditWorker() {
	for entry := range auditChan {
		mu.Lock()
		_, err := db.Exec("INSERT INTO audit_log (timestamp, hash, pii_detected) VALUES (?, ?, ?)", 
			entry.Timestamp, entry.Hash, entry.PII)
		if err != nil {
			log.Printf("audit flush error: %v", err)
		}
		mu.Unlock()
	}
}

func auditRequest(req *http.Request) {
	// 150ms timeout for audit process
	done := make(chan bool, 1)
	go func() {
		body, _ := io.ReadAll(req.Body)
		h := hmac.New(sha256.New, []byte(os.Getenv("SOVEREIGN_KEY")))
		h.Write(body)
		
		auditChan <- AuditEntry{
			Timestamp: time.Now().Format(time.RFC3339),
			Hash:      hex.EncodeToString(h.Sum(nil)),
			PII:       krnRegex.Match(body),
		}
		done <- true
	}()

	select {
	case <-done:
	case <-time.After(150 * time.Millisecond):
		log.Println("lat-warn: audit dropped")
	}
}

func main() {
	target, _ := url.Parse("https://api.k-cloud-provider.com")
	proxy := httputil.NewSingleHostReverseProxy(target)
	proxy.Director = func(req *http.Request) {
		req.URL.Scheme = target.Scheme
		req.URL.Host = target.Host
		auditRequest(req)
	}
	log.Fatal(http.ListenAndServe(":8080", proxy))
}
