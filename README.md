# Network Port Scanner GUI

A lightweight TCP port scanner with a graphical user interface built with Python and Tkinter.

## Features
- Simple 3-field interface – enter a target host, start port, and end port
- Multi-threaded scanning – up to 500 concurrent threads for fast results
- Service identification – automatically labels well-known ports (FTP, SSH, HTTP, HTTPS, MySQL, RDP, etc.)
- Real-time progress – progress bar and elapsed-time counter update live during a scan
- Stop at any time – cancel a running scan gracefully
- Save results – export discovered open ports to a `.txt` file
- Cross-platform – runs on Windows, macOS, and Linux

## Requirements
- Python 3.7 or newer
- Tkinter (included in the standard Python distribution; on Debian/Ubuntu install `python3-tk`)

> No third-party packages are required.

## Installation
```bash
git clone https://github.com/aarishkhan2361/network-port-scanner.git
cd network-port-scanner
```

## Usage
```bash
python portscanergui.py
```

1. Enter the **Target** – an IP address (e.g. `192.168.1.1`) or hostname (e.g. `scanme.nmap.org`)
2. Set the **Start Port** and **End Port** (defaults: `1` – `1024`)
3. Click **Start Scan** – open ports appear in real time in the results pane
4. Click **Stop** to cancel a scan early
5. After a scan completes, click **Save Results** to write the open-port list to a text file

## Detected Services

| Port | Service  |
|------|----------|
| 21   | FTP      |
| 22   | SSH      |
| 23   | Telnet   |
| 25   | SMTP     |
| 53   | DNS      |
| 80   | HTTP     |
| 110  | POP3     |
| 143  | IMAP     |
| 443  | HTTPS    |
| 3306 | MySQL    |
| 3389 | RDP      |
| 5900 | VNC      |
| 8080 | HTTP-Alt |

> Ports not in the list are reported as `Unknown`.

## Project Structure
```
network-port-scanner/
├── portscanergui.py   # Main application (scanner + GUI)
├── README.md
└── Network_Port_Scanner_Project_AarishKhan.pptx
```

## Disclaimer
> ⚠️ Use this tool only on hosts and networks you own or have explicit permission to scan.
> Unauthorized port scanning may be illegal in your jurisdiction.

## License
This project is released under the **MIT License**.

## Credits
- Original project by [techtrainer20](https://github.com/techtrainer20/nmap_portscan_gui)
- Modified and submitted by **Aarish Khan**
- AICTE ID: **STU6823b63f41f6c1747170879**
- Submitted for **AICTE Internship 2026**
