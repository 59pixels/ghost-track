import sys
import os
import time
import socket
import numpy as np
import json
from pathlib import Path

# Add micro-espectre to path
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.append(str(project_root / "micro-espectre"))

from tools.csi_utils import CSIReceiver, CSIPacket

class MultiNodeCollector:
    def __init__(self, port=5001):
        self.port = port
        self.receiver = CSIReceiver(port=port)
        self.node_data = {}  # IP -> List of packets
        self.node_mapping = {} # IP -> Node Name (Node 1, Node 2, etc.)
        self.start_time = None
        
    def packet_callback(self, packet):
        # In a real UDP stream, addr is not in CSIPacket by default in csi_utils
        # We need to modify CSIReceiver or use a custom listener
        pass

    def run_discovery(self, duration=5):
        """Listen for a few seconds to discover active nodes on the network"""
        print(f"📡 Discovering nodes on port {self.port} for {duration} seconds...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', self.port))
        sock.settimeout(1.0)
        
        found_ips = set()
        start = time.time()
        while time.time() - start < duration:
            try:
                data, addr = sock.recvfrom(1024)
                if addr[0] not in found_ips:
                    print(f"  ✅ Found node at {addr[0]}")
                    found_ips.add(addr[0])
            except socket.timeout:
                continue
        
        sock.close()
        return sorted(list(found_ips))

    def start_sync_collection(self, nodes, duration=10, output_file="sample.npz"):
        """Collect synchronized data from specified nodes"""
        print(f"\n🚀 Starting synchronized collection for {duration}s...")
        print(f"Nodes: {', '.join(nodes)}")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', self.port))
        sock.settimeout(0.5)
        
        data_store = {ip: [] for ip in nodes}
        start = time.time()
        
        try:
            while time.time() - start < duration:
                try:
                    data, addr = sock.recvfrom(1024)
                    ip = addr[0]
                    if ip in data_store:
                        packet = self.receiver._parse_packet(data)
                        if packet:
                            data_store[ip].append({
                                'ts': time.time(),
                                'seq': packet.seq_num,
                                'amplitudes': packet.amplitudes
                            })
                except socket.timeout:
                    continue
            
            print("\n✅ Collection complete!")
            for ip, pkts in data_store.items():
                print(f"  Node {ip}: {len(pkts)} packets collected")
                
            # Basic sync logic: save all
            # (In Phase 3 we will do the heavy interpolation/sync)
            save_data = {}
            for i, ip in enumerate(nodes):
                save_data[f"node_{i+1}_csi"] = np.array([p['amplitudes'] for p in data_store[ip]])
                save_data[f"node_{i+1}_ts"] = np.array([p['ts'] for p in data_store[ip]])
            
            np.savez_compressed(output_file, **save_data)
            print(f"💾 Data saved to {output_file}")
            
        finally:
            sock.close()

if __name__ == "__main__":
    collector = MultiNodeCollector()
    ips = collector.run_discovery(duration=60)
    
    if len(ips) < 4:
        print(f"\n⚠️ Warning: Only found {len(ips)} nodes. We need 4 for 3D tracking.")
        if len(ips) == 0:
            print("❌ No nodes found. Make sure they are streaming!")
            sys.exit(1)
            
    # For now, just collect a test sample
    collector.start_sync_collection(ips, duration=10, output_file="3d-tracking/test_stream.npz")
