package main

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"io"
	"log"
	"os"
	"sync"
)

// LedgerEntry represents a single cryptographically chained event
type LedgerEntry struct {
	Timestamp string
	PayloadHash string
	PrevHash    string
	PIIViolation bool
}

type AuditLedger struct {
	mu       sync.Mutex
	lastHash string
	filePath string
}

func NewLedger(path string) *AuditLedger {
	return &AuditLedger{filePath: path, lastHash: "00000000000000000000000000000000"}
}

func (l *AuditLedger) Append(data []byte, pii bool) (string, error) {
	l.mu.Lock()
	defer l.mu.Unlock()

	h := sha256.New()
	h.Write(data)
	h.Write([]byte(l.lastHash))
	newHash := hex.EncodeToString(h.Sum(nil))

	entry := fmt.Sprintf("%s|%s|%t|%s\n", 
		time.Now().Format(time.RFC3339), newHash, pii, l.lastHash)
	
	f, _ := os.OpenFile(l.filePath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	defer f.Close()
	f.WriteString(entry)
	
	l.lastHash = newHash
	return newHash, nil
}
