# Multithreaded Python HTTP/HTTPS Server

Ein einfacher, multithreaded Python-Server mit Unterstützung für HTTP und HTTPS (SSL).

## Features

- **Multithreading**: Bearbeitet mehrere Client-Anfragen gleichzeitig.
- **HTTPS-Unterstützung**: Einfache Aktivierung von sicherer Kommunikation über SSL/TLS.
- **Thread-Info**: Antwortet mit Thread-Namen und der Anzahl der aktiven Threads.
- **Leicht anpassbar**: Kann einfach erweitert und für spezifische Anwendungsfälle modifiziert werden.

## Voraussetzungen

- Python 3.7 oder neuer
- Optional: SSL-Zertifikat und privater Schlüssel (`cert.pem` und `key.pem`) für HTTPS

## Installation

1. Klone das Repository:
   ```bash
   git clone <REPO-URL>
   cd <REPO-NAME>
