# Installations
- `python3 -m venv venv`
- `source venv/bin/activate`
- `pip install -r requirements.txt`

# Run teacher (server) code
- `source venv/bin/activate`
- `python3 teacher/mainServer.py`

# Run student (client) code
- `source venv/bin/activate`
- `python3 student mainClient.py`
- Enter `[name]` and `[id]`
- Enter password to give sudo access for port scanning.
- Press enter to start screen capture. 

# Feature Description

## QnA

## Port Scanning
- Runs `sudo lsof -i -P -n` on the command line and retrieves connections involving a `LISTEN` or `ESTABLISHED` port.
- Client sends login particulars to server, to initiate connection.
- Server acknowledges with `ACK`, and starts requesting for port information from client every 10s.

### Check for unauthorised connections
- Upon receiving client port information, server parses it and checks for potential unauthorised connections.
    - Processes involving MAC, localhost and loopback addresses are filtered out as they are assumed to be necessary background processes.
    - Even though some unauthorised connections also run such processes, these connections also connect with non-local IP addresses, which can be detected in the next step.
- The port number of the remaining processes are extracted and compared against ports opened by this program.
    - If the port number does not match any of the program's ports, the connection is deemed unauthorised and the relevant app is identified.
- A list of unauthorised apps is subsequently returned and printed on both the server and client screens.

## Screen Capture
