# Multithreaded Python HTTP Server

Ein einfacher, multithreaded Python-Server mit Benutzerregistrierung, Login und Session-Management.

## Features

- **Multithreading**: Bearbeitet mehrere Client-Anfragen gleichzeitig.
- **Session-Management**: Nutzer können sich registrieren, anmelden und ihre Sitzungen verwalten.
- **Sichere Passwortspeicherung**: Passwörter werden mit SHA-256 gehasht.
- **Datenspeicherung**: Benutzerinformationen werden in einer JSON-Datei gespeichert.

## Voraussetzungen

- Python 3.7 oder neuer

## Installation

1. Klone das Repository:
   ```bash
   git clone <REPO-URL>
   cd <REPO-NAME>
   ```

2. Starte den Server:
   ```bash
   python server.py
   ```

## Endpunkte

### Registrierung
**POST /register**
- **Body:** `{ "username": "testuser", "password": "testpass" }`
- **Antwort:** `{ "message": "User registered successfully" }`

### Login
**POST /login**
- **Body:** `{ "username": "testuser", "password": "testpass" }`
- **Antwort:** `{ "message": "Login successful" }` (Setzt Session-Cookie)

### Wert speichern
**POST /write**
- **Body:** `{ "varname": "color", "value": "blue" }`
- **Antwort:** `{ "message": "Value stored", "color": "blue" }`

### Wert abrufen
**GET /read/{varname}**
- **Antwort:** `{ "color": "blue" }` oder `{ "error": "Unauthorized" }`

## Multithreading
Der Server nutzt `ThreadingTCPServer`, um mehrere Anfragen gleichzeitig zu verarbeiten, sowie ein `threading.Lock`, um gleichzeitige Zugriffe auf `session_store` zu synchronisieren.


