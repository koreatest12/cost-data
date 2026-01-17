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
        self.firewall_rules = {}
        self.load_config()
    
    def load_config(self):
        """Load server configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        data = json.loads(content)
                        self.servers = data.get('servers', {})
                        self.firewall_rules = data.get('firewall_rules', {})
                    else:
                        self.servers = {}
                        self.firewall_rules = {}
            except json.JSONDecodeError:
                self.servers = {}
                self.firewall_rules = {}
        else:
            self.servers = {}
            self.firewall_rules = {}
    
    def save_config(self):
        """Save server configuration to file"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            data = {
                'servers': self.servers,
                'firewall_rules': self.firewall_rules
            }
            json.dump(data, f, indent=2, ensure_ascii=False)
    
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
    
    def add_firewall_rule(self, server_id: str, rule: Dict) -> Dict:
        """
        Add firewall rule to a server
        Supports both inbound and outbound rules with port and protocol specifications
        """
        if server_id not in self.servers:
            raise ValueError(f"Server {server_id} not found")
        
        if server_id not in self.firewall_rules:
            self.firewall_rules[server_id] = []
        
        rule_id = f"rule-{len(self.firewall_rules[server_id]) + 1}"
        
        firewall_rule = {
            "id": rule.get("id", rule_id),
            "name": rule.get("name", f"Rule {rule_id}"),
            "protocol": rule.get("protocol", "TCP"),
            "port": rule.get("port", 80),
            "direction": rule.get("direction", "inbound"),
            "action": rule.get("action", "allow"),
            "source": rule.get("source", "any"),
            "destination": rule.get("destination", "any"),
            "created_at": datetime.now().isoformat()
        }
        
        self.firewall_rules[server_id].append(firewall_rule)
        self.save_config()
        
        return {
            "server_id": server_id,
            "rule": firewall_rule,
            "total_rules": len(self.firewall_rules[server_id])
        }
    
    def remove_firewall_rule(self, server_id: str, rule_id: str) -> Dict:
        """Remove a firewall rule from a server"""
        if server_id not in self.servers:
            raise ValueError(f"Server {server_id} not found")
        
        if server_id not in self.firewall_rules:
            raise ValueError(f"No firewall rules found for server {server_id}")
        
        original_count = len(self.firewall_rules[server_id])
        self.firewall_rules[server_id] = [
            r for r in self.firewall_rules[server_id] if r["id"] != rule_id
        ]
        
        removed = len(self.firewall_rules[server_id]) < original_count
        
        if removed:
            self.save_config()
            return {
                "server_id": server_id,
                "rule_id": rule_id,
                "removed": True,
                "remaining_rules": len(self.firewall_rules[server_id])
            }
        else:
            raise ValueError(f"Firewall rule {rule_id} not found")
    
    def list_firewall_rules(self, server_id: str) -> List[Dict]:
        """List all firewall rules for a server"""
        if server_id not in self.servers:
            raise ValueError(f"Server {server_id} not found")
        
        return self.firewall_rules.get(server_id, [])
    
    def install_firewall(self, server_id: str, firewall_type: str = "ufw") -> Dict:
        """
        Install and configure firewall on a server
        Supports UFW (Linux), Windows Firewall, and iptables
        """
        if server_id not in self.servers:
            raise ValueError(f"Server {server_id} not found")
        
        server = self.servers[server_id]
        
        # Initialize firewall configuration
        firewall_config = {
            "type": firewall_type,
            "installed": True,
            "installed_at": datetime.now().isoformat(),
            "enabled": True,
            "default_policy": "deny"
        }
        
        # Add default rules based on firewall type
        default_rules = []
        if firewall_type.lower() == "ufw":
            default_rules = [
                {"name": "SSH", "protocol": "TCP", "port": 22, "direction": "inbound", "action": "allow"},
                {"name": "HTTP", "protocol": "TCP", "port": 80, "direction": "inbound", "action": "allow"},
                {"name": "HTTPS", "protocol": "TCP", "port": 443, "direction": "inbound", "action": "allow"}
            ]
        elif firewall_type.lower() == "windows":
            default_rules = [
                {"name": "RDP", "protocol": "TCP", "port": 3389, "direction": "inbound", "action": "allow"},
                {"name": "HTTP", "protocol": "TCP", "port": 80, "direction": "inbound", "action": "allow"},
                {"name": "HTTPS", "protocol": "TCP", "port": 443, "direction": "inbound", "action": "allow"}
            ]
        
        # Add firewall configuration to server
        server["firewall"] = firewall_config
        
        # Add default rules
        if server_id not in self.firewall_rules:
            self.firewall_rules[server_id] = []
        
        for rule in default_rules:
            rule["id"] = f"rule-{len(self.firewall_rules[server_id]) + 1}"
            rule["source"] = "any"
            rule["destination"] = "any"
            rule["created_at"] = datetime.now().isoformat()
            self.firewall_rules[server_id].append(rule)
        
        self.save_config()
        
        return {
            "server_id": server_id,
            "firewall": firewall_config,
            "default_rules_added": len(default_rules),
            "total_rules": len(self.firewall_rules[server_id])
        }
    
    def upgrade_firewall(self, server_id: str, upgrade_config: Dict) -> Dict:
        """
        Upgrade firewall configuration with enhanced security features
        """
        if server_id not in self.servers:
            raise ValueError(f"Server {server_id} not found")
        
        server = self.servers[server_id]
        
        if "firewall" not in server:
            raise ValueError(f"Firewall not installed on server {server_id}")
        
        upgrade_info = {
            "timestamp": datetime.now().isoformat(),
            "upgrades": []
        }
        
        # Enable advanced features
        if upgrade_config.get("enable_ddos_protection"):
            server["firewall"]["ddos_protection"] = True
            upgrade_info["upgrades"].append("DDoS protection enabled")
        
        if upgrade_config.get("enable_intrusion_detection"):
            server["firewall"]["intrusion_detection"] = True
            upgrade_info["upgrades"].append("Intrusion detection enabled")
        
        if upgrade_config.get("enable_rate_limiting"):
            server["firewall"]["rate_limiting"] = {
                "enabled": True,
                "max_connections": upgrade_config.get("max_connections", 100)
            }
            upgrade_info["upgrades"].append("Rate limiting enabled")
        
        if upgrade_config.get("enable_geo_blocking"):
            server["firewall"]["geo_blocking"] = {
                "enabled": True,
                "blocked_countries": upgrade_config.get("blocked_countries", [])
            }
            upgrade_info["upgrades"].append("Geo-blocking enabled")
        
        # Record upgrade in history
        if "firewall_upgrade_history" not in server:
            server["firewall_upgrade_history"] = []
        
        server["firewall_upgrade_history"].append(upgrade_info)
        self.save_config()
        
        return {
            "server_id": server_id,
            "upgrade_info": upgrade_info,
            "firewall_config": server["firewall"]
        }


def main():
    """CLI interface for server management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Server Management System")
    parser.add_argument("action", choices=[
        "add", "upgrade", "check-capacity", "expand-capacity", 
        "install-disk", "add-disk", "info", "list",
        "install-firewall", "upgrade-firewall", "add-firewall-rule", 
        "remove-firewall-rule", "list-firewall-rules"
    ], help="Action to perform")
    parser.add_argument("--server-id", help="Server ID")
    parser.add_argument("--cpu", type=int, help="CPU cores")
    parser.add_argument("--memory", type=int, help="Memory in GB")
    parser.add_argument("--disk-size", type=int, help="Disk size in GB")
    parser.add_argument("--disk-type", default="SSD", help="Disk type (SSD/HDD)")
    parser.add_argument("--expansion-type", choices=["cpu", "memory", "disk"], help="Type of capacity to expand")
    parser.add_argument("--amount", type=int, help="Amount to expand")
    parser.add_argument("--firewall-type", default="ufw", choices=["ufw", "windows", "iptables"], help="Firewall type")
    parser.add_argument("--rule-name", help="Firewall rule name")
    parser.add_argument("--protocol", default="TCP", help="Protocol (TCP/UDP)")
    parser.add_argument("--port", type=int, help="Port number")
    parser.add_argument("--direction", default="inbound", choices=["inbound", "outbound"], help="Rule direction")
    parser.add_argument("--action", default="allow", choices=["allow", "deny"], help="Rule action")
    parser.add_argument("--rule-id", help="Rule ID to remove")
    parser.add_argument("--enable-ddos", action="store_true", help="Enable DDoS protection")
    parser.add_argument("--enable-ids", action="store_true", help="Enable intrusion detection")
    parser.add_argument("--enable-rate-limit", action="store_true", help="Enable rate limiting")
    
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
        
        elif args.action == "install-firewall":
            if not args.server_id:
                print("Error: --server-id required")
                return
            
            result = manager.install_firewall(args.server_id, args.firewall_type)
            print(f"Firewall installed: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        elif args.action == "upgrade-firewall":
            if not args.server_id:
                print("Error: --server-id required")
                return
            
            upgrade_config = {
                "enable_ddos_protection": args.enable_ddos,
                "enable_intrusion_detection": args.enable_ids,
                "enable_rate_limiting": args.enable_rate_limit
            }
            result = manager.upgrade_firewall(args.server_id, upgrade_config)
            print(f"Firewall upgraded: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        elif args.action == "add-firewall-rule":
            if not args.server_id:
                print("Error: --server-id required")
                return
            
            rule = {
                "name": args.rule_name or f"Rule-{args.port}",
                "protocol": args.protocol,
                "port": args.port or 80,
                "direction": args.direction,
                "action": args.action
            }
            result = manager.add_firewall_rule(args.server_id, rule)
            print(f"Firewall rule added: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        elif args.action == "remove-firewall-rule":
            if not args.server_id or not args.rule_id:
                print("Error: --server-id and --rule-id required")
                return
            
            result = manager.remove_firewall_rule(args.server_id, args.rule_id)
            print(f"Firewall rule removed: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        elif args.action == "list-firewall-rules":
            if not args.server_id:
                print("Error: --server-id required")
                return
            
            result = manager.list_firewall_rules(args.server_id)
            print(f"Firewall rules: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
