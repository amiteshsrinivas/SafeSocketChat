# SafeSocketChat

A secure, end-to-end encrypted chat application for two clients, featuring a modern GUI and robust logging. Communication is encrypted using ECC (X25519) for key exchange and AES-GCM for message confidentiality.

---

## Features
- **End-to-end encryption** using X25519 and AES-GCM
- **Modern GUI** built with CustomTkinter
- **Message logging** with encryption details
- **Multithreaded server** for real-time chat
- **Easy setup** for local or LAN use

---

## Screenshots

### Chat Client Window
![Chat Client Window](screenshots/client.png)

### Server Terminal
![Server Terminal](screenshots/server.png)

---

## Project Structure
```
SafeSocketChat/
├── client1.py           # Chat client 1 (GUI)
├── client2.py           # Chat client 2 (GUI)
├── Server.py            # Multithreaded chat server
├── ECC.py               # ECC and AES-GCM cryptography utilities
├── message_logger.py    # Message logging utility
├── message_logs/        # Directory for per-user message logs
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

---

## Requirements
- Python 3.8+
- See `requirements.txt` for dependencies:
  - cryptography>=41.0.0
  - customtkinter>=5.2.0
  - Pillow>=10.0.0

Install dependencies with:
```bash
pip install -r requirements.txt
```

---

## Logging
- All message exchanges, public key handshakes, and errors are logged in `message_logs/{your_name}_messages.log`.
- Logs include timestamps, plain/cipher text, and shared key (hex).

---

## Security
- Uses X25519 for key exchange and AES-GCM for message encryption.
- No plaintext messages are sent over the network.

---

## Notes
- The `venv/` directory is for your local Python virtual environment and should not be committed.
- You can run both clients on the same or different machines.
- For screenshots, create a `screenshots/` folder and add images as needed.

---

## License
MIT License 