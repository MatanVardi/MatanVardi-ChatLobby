# Chat Application

A Python-based real-time chat application that supports both local and network communication between multiple clients.

## Features

- 🔐 User registration and authentication
- 💬 Real-time messaging
- 👥 Multi-client support
- 🌐 Local and network deployment options
- 🔒 Encrypted password storage
- 📝 Chat history persistence
- 🖥️ GUI-based client interface

## Architecture

This application consists of two main components:

- **Server** (`run_server.py`) - Handles client connections and message routing
- **Client** (`app.py`) - Provides the user interface for chatting

## Prerequisites

- Python 3.x
- Required Python packages

## Quick Start

### Single Computer Setup (Testing)

Perfect for testing the application on one machine:

1. **Start the server:**
   ```bash
   python run_server.py
   ```

2. **Start the client in a new terminal:**
   ```bash
   python app.py
   ```

3. Login/register and start chatting locally!

### Multi-Computer Setup

For real network communication between different computers:

#### Step 1: Start the Server
On the computer that will act as the server:
```bash
python run_server.py
```
📝 **Important:** Note the IPv4 address displayed - clients will need this to connect.

#### Step 2: Start Client(s)
On each client computer:
```bash
python app.py
```
- Login with existing credentials or register a new account
- Enter the server's IP address when prompted
- Start chatting!

## Network Requirements

The application works with these network configurations:

### Option 1: Same WiFi Network
- Connect all computers to the same WiFi network
- The server automatically detects and displays the correct IP address
- Clients use this IP to connect

### Option 2: LAN Cable Connection
- Connect computers using Ethernet/LAN cable
- Configure Windows network settings:
  1. Go to **Control Panel** → **Network and Sharing Center**
  2. Click **"Change advanced sharing settings"**
  3. Enable network discovery and file sharing
  4. Ensure both computers are on the same network profile

## Database

The application uses a local database to store:
- User account information
- Chat history and logs

You can open the database file with any SQLite browser to view the stored data.

## Test Account

A pre-configured test account is available for quick testing:
- **Username:** `testuser`
- **Password:** `testpass123`

## Troubleshooting

### Connection Issues
- ✅ Ensure firewall isn't blocking the application
- ✅ Verify all computers are on the same network
- ✅ Check that the server IP address is entered correctly
- ✅ For LAN connections, verify network sharing settings are enabled

### Server Not Starting
- ✅ Check if the port is already in use
- ✅ Ensure Python has necessary permissions
- ✅ Verify all required dependencies are installed

## Technical Details

- **Protocol:** TCP socket communication
- **GUI Framework:** Tkinter (or specify your framework)
- **Database:** SQLite
- **Encryption:** Password hashing for security
- **Port:** 12345 (default, configurable)

## File Structure

```
chat-application/
├── run_server.py      # Server script
├── app.py            # Client GUI application
├── requirements.txt  # Python dependencies
├── database.db       # SQLite database (created automatically)
└── README.md         # This file
```

