import socket

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to all interfaces on port 5001
try:
    sock.bind(('0.0.0.0', 5001))
    print("\n🛰️  RADIO SCANNER ACTIVE")
    print("------------------------------------------")
    print("Listening for any CSI packets on Port 5001...")
    print("Press Ctrl+C to stop.")
    print("------------------------------------------\n")

    while True:
        data, addr = sock.recvfrom(1024)
        print(f"✅ SIGNAL DETECTED! Received {len(data)} bytes from {addr[0]}")
except Exception as e:
    print(f"❌ Error binding to port 5001: {e}")
    print("Make sure no other collector scripts or scanners are running!")
finally:
    sock.close()
