#!/usr/bin/env python3
"""
Server Management System
Provides server upgrade, capacity check, capacity expansion, disk installation, and disk management features
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class ServerManager:
    """Main class for managing server operations"""
    
    def __init__(self, config_file: str = "server_config.json"):
        """Initialize ServerManager with configuration file"""
        self.config_file = config_file
        self.servers = {}
        self.load_config()
    
    def load_config(self):
        """Load server configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        self.servers = json.loads(content)
                    else:
                        self.servers = {}
            except json.JSONDecodeError:
                self.servers = {}
        else:
            self.servers = {}
    
    def save_config(self):
        """Save server configuration to file"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.servers, f, indent=2, ensure_ascii=False)
    
    def add_server(self, server_id: str, specs: Dict):
        """Add a new server to the management system"""
        if server_id in self.servers:
            raise ValueError(f"Server {server_id} already exists")
        
        self.servers[server_id] = {
            "id": server_id,
            "cpu": specs.get("cpu", 2),
            "memory_gb": specs.get("memory_gb", 4),
            "disks": specs.get("disks", []),
            "os": specs.get("os", "Linux"),
            "created_at": datetime.now().isoformat(),
            "upgrade_history": [],
            "disk_history": []
        }
        self.save_config()
        return self.servers[server_id]
    
    def upgrade_server(self, server_id: str, upgrade_specs: Dict) -> Dict:
        """
        Server upgrade configuration feature
        Upgrades server CPU, memory, or other specifications
        """
        if server_id not in self.servers:
            raise ValueError(f"Server {server_id} not found")
        
        server = self.servers[server_id]
        upgrade_info = {
            "timestamp": datetime.now().isoformat(),
            "changes": {}
        }
        
        # Upgrade CPU
        if "cpu" in upgrade_specs:
            old_cpu = server["cpu"]
            new_cpu = upgrade_specs["cpu"]
            if new_cpu > old_cpu:
                server["cpu"] = new_cpu
                upgrade_info["changes"]["cpu"] = {
                    "from": old_cpu,
                    "to": new_cpu
                }
        
        # Upgrade Memory
        if "memory_gb" in upgrade_specs:
            old_memory = server["memory_gb"]
            new_memory = upgrade_specs["memory_gb"]
            if new_memory > old_memory:
                server["memory_gb"] = new_memory
                upgrade_info["changes"]["memory_gb"] = {
                    "from": old_memory,
                    "to": new_memory
                }
        
        # Record upgrade in history
        server["upgrade_history"].append(upgrade_info)
        self.save_config()
        
        return {
            "server_id": server_id,
            "upgrade_info": upgrade_info,
            "current_specs": {
                "cpu": server["cpu"],
                "memory_gb": server["memory_gb"]
            }
        }
    
    def check_capacity(self, server_id: str) -> Dict:
        """
        Capacity check feature
        Checks current server capacity and usage
        """
        if server_id not in self.servers:
            raise ValueError(f"Server {server_id} not found")
        
        server = self.servers[server_id]
        
        # Calculate total disk capacity
        total_disk_capacity = sum(disk.get("size_gb", 0) for disk in server.get("disks", []))
        
        return {
            "server_id": server_id,
            "cpu_cores": server["cpu"],
            "memory_gb": server["memory_gb"],
            "total_disk_gb": total_disk_capacity,
            "disk_count": len(server.get("disks", [])),
            "disks": server.get("disks", [])
        }
    
    def expand_capacity(self, server_id: str, expansion_type: str, amount: int) -> Dict:
        """
        Capacity expansion feature
        Expands server capacity (CPU, memory, or disk)
        """
        if server_id not in self.servers:
            raise ValueError(f"Server {server_id} not found")
        
        server = self.servers[server_id]
        expansion_info = {
            "timestamp": datetime.now().isoformat(),
            "type": expansion_type,
            "amount": amount
        }
        
        if expansion_type == "cpu":
            old_cpu = server["cpu"]
            server["cpu"] += amount
            expansion_info["old_value"] = old_cpu
            expansion_info["new_value"] = server["cpu"]
        
        elif expansion_type == "memory":
            old_memory = server["memory_gb"]
            server["memory_gb"] += amount
            expansion_info["old_value"] = old_memory
            expansion_info["new_value"] = server["memory_gb"]
        
        elif expansion_type == "disk":
            # For disk expansion, we expand the first disk or largest disk
            if server.get("disks"):
                # Find largest disk and expand it
                largest_disk = max(server["disks"], key=lambda d: d.get("size_gb", 0))
                old_size = largest_disk["size_gb"]
                largest_disk["size_gb"] += amount
                expansion_info["disk_id"] = largest_disk["id"]
                expansion_info["old_value"] = old_size
                expansion_info["new_value"] = largest_disk["size_gb"]
        
        # Record in upgrade history
        if "upgrade_history" not in server:
            server["upgrade_history"] = []
        server["upgrade_history"].append({
            "timestamp": expansion_info["timestamp"],
            "type": "capacity_expansion",
            "details": expansion_info
        })
        
        self.save_config()
        return expansion_info
    
    def install_disk(self, server_id: str, disk_specs: Dict) -> Dict:
        """
        Disk installation feature
        Installs a new disk on the server
        """
        if server_id not in self.servers:
            raise ValueError(f"Server {server_id} not found")
        
        server = self.servers[server_id]
        
        if "disks" not in server:
            server["disks"] = []
        
        # Generate disk ID
        disk_id = f"disk-{len(server['disks']) + 1}"
        
        new_disk = {
            "id": disk_specs.get("id", disk_id),
            "size_gb": disk_specs.get("size_gb", 100),
            "type": disk_specs.get("type", "SSD"),
            "mount_point": disk_specs.get("mount_point", f"/mnt/{disk_id}"),
            "installed_at": datetime.now().isoformat()
        }
        
        server["disks"].append(new_disk)
        
        # Record in disk history
        if "disk_history" not in server:
            server["disk_history"] = []
        
        server["disk_history"].append({
            "timestamp": datetime.now().isoformat(),
            "action": "install",
            "disk": new_disk
        })
        
        self.save_config()
        
        return {
            "server_id": server_id,
            "disk": new_disk,
            "total_disks": len(server["disks"])
        }
    
    def add_disk(self, server_id: str, disk_specs: Dict) -> Dict:
        """
        Disk addition reflection feature
        Adds and reflects a disk to the server configuration
        """
        # This is an alias for install_disk with additional reflection/validation
        result = self.install_disk(server_id, disk_specs)
        
        # Additional reflection: verify the disk was added
        server = self.servers[server_id]
        disk_found = any(d["id"] == result["disk"]["id"] for d in server["disks"])
        
        result["reflected"] = disk_found
        result["reflection_timestamp"] = datetime.now().isoformat()
        
        return result
    
    def get_server_info(self, server_id: str) -> Dict:
        """Get detailed server information"""
        if server_id not in self.servers:
            raise ValueError(f"Server {server_id} not found")
        
        return self.servers[server_id]
    
    def list_servers(self) -> List[Dict]:
        """List all servers"""
        return list(self.servers.values())


def main():
    """CLI interface for server management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Server Management System")
    parser.add_argument("action", choices=[
        "add", "upgrade", "check-capacity", "expand-capacity", 
        "install-disk", "add-disk", "info", "list"
    ], help="Action to perform")
    parser.add_argument("--server-id", help="Server ID")
    parser.add_argument("--cpu", type=int, help="CPU cores")
    parser.add_argument("--memory", type=int, help="Memory in GB")
    parser.add_argument("--disk-size", type=int, help="Disk size in GB")
    parser.add_argument("--disk-type", default="SSD", help="Disk type (SSD/HDD)")
    parser.add_argument("--expansion-type", choices=["cpu", "memory", "disk"], help="Type of capacity to expand")
    parser.add_argument("--amount", type=int, help="Amount to expand")
    
    args = parser.parse_args()
    
    manager = ServerManager()
    
    try:
        if args.action == "add":
            if not args.server_id:
                print("Error: --server-id required")
                return
            
            specs = {
                "cpu": args.cpu or 2,
                "memory_gb": args.memory or 4,
                "disks": []
            }
            result = manager.add_server(args.server_id, specs)
            print(f"Server added: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        elif args.action == "upgrade":
            if not args.server_id:
                print("Error: --server-id required")
                return
            
            upgrade_specs = {}
            if args.cpu:
                upgrade_specs["cpu"] = args.cpu
            if args.memory:
                upgrade_specs["memory_gb"] = args.memory
            
            result = manager.upgrade_server(args.server_id, upgrade_specs)
            print(f"Server upgraded: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        elif args.action == "check-capacity":
            if not args.server_id:
                print("Error: --server-id required")
                return
            
            result = manager.check_capacity(args.server_id)
            print(f"Capacity info: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        elif args.action == "expand-capacity":
            if not args.server_id or not args.expansion_type or not args.amount:
                print("Error: --server-id, --expansion-type, and --amount required")
                return
            
            result = manager.expand_capacity(args.server_id, args.expansion_type, args.amount)
            print(f"Capacity expanded: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        elif args.action == "install-disk":
            if not args.server_id:
                print("Error: --server-id required")
                return
            
            disk_specs = {
                "size_gb": args.disk_size or 100,
                "type": args.disk_type
            }
            result = manager.install_disk(args.server_id, disk_specs)
            print(f"Disk installed: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        elif args.action == "add-disk":
            if not args.server_id:
                print("Error: --server-id required")
                return
            
            disk_specs = {
                "size_gb": args.disk_size or 100,
                "type": args.disk_type
            }
            result = manager.add_disk(args.server_id, disk_specs)
            print(f"Disk added and reflected: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        elif args.action == "info":
            if not args.server_id:
                print("Error: --server-id required")
                return
            
            result = manager.get_server_info(args.server_id)
            print(f"Server info: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        elif args.action == "list":
            result = manager.list_servers()
            print(f"All servers: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
