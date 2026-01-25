#!/usr/bin/env python3
"""
Server Management System v2.0
Provides server upgrade, capacity check, disk management,
bulk customer registration, table creation, and data loading features.
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Union

class ServerManager:
    """Main class for managing server operations and data"""
    
    def __init__(self, config_file: str = "server_config.json"):
        """Initialize ServerManager with configuration file"""
        self.config_file = config_file
        self.data = {
            "servers": {},
            "customers": []
        }
        self.load_config()
    
    def load_config(self):
        """Load configuration with backward compatibility"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        loaded_data = json.loads(content)
                        # Migration logic: Check if it's the old format (keys are server IDs)
                        # or new format (keys include 'servers', 'customers')
                        if "servers" in loaded_data and isinstance(loaded_data["servers"], dict):
                            self.data = loaded_data
                        else:
                            # Migrate old format to new format
                            self.data["servers"] = loaded_data
                            self.data["customers"] = []
                    else:
                        self._init_empty_data()
            except json.JSONDecodeError:
                self._init_empty_data()
        else:
            self._init_empty_data()
    
    def _init_empty_data(self):
        self.data = {"servers": {}, "customers": []}

    def save_config(self):
        """Save current state to file"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    # ==========================
    # Server Management Methods
    # ==========================

    def add_server(self, server_id: str, specs: Dict):
        if server_id in self.data["servers"]:
            raise ValueError(f"Server {server_id} already exists")
        
        self.data["servers"][server_id] = {
            "id": server_id,
            "cpu": specs.get("cpu", 2),
            "memory_gb": specs.get("memory_gb", 4),
            "disks": specs.get("disks", []),
            "tables": {},  # New: Container for database tables
            "os": specs.get("os", "Linux"),
            "created_at": datetime.now().isoformat(),
            "upgrade_history": [],
            "disk_history": []
        }
        self.save_config()
        return self.data["servers"][server_id]
    
    def upgrade_server(self, server_id: str, upgrade_specs: Dict) -> Dict:
        if server_id not in self.data["servers"]:
            raise ValueError(f"Server {server_id} not found")
        
        server = self.data["servers"][server_id]
        upgrade_info = {
            "timestamp": datetime.now().isoformat(),
            "changes": {}
        }
        
        if "cpu" in upgrade_specs:
            old_cpu = server["cpu"]
            if upgrade_specs["cpu"] > old_cpu:
                server["cpu"] = upgrade_specs["cpu"]
                upgrade_info["changes"]["cpu"] = {"from": old_cpu, "to": server["cpu"]}
        
        if "memory_gb" in upgrade_specs:
            old_mem = server["memory_gb"]
            if upgrade_specs["memory_gb"] > old_mem:
                server["memory_gb"] = upgrade_specs["memory_gb"]
                upgrade_info["changes"]["memory_gb"] = {"from": old_mem, "to": server["memory_gb"]}
        
        server["upgrade_history"].append(upgrade_info)
        self.save_config()
        return {"server_id": server_id, "upgrade_info": upgrade_info}

    def check_capacity(self, server_id: str) -> Dict:
        if server_id not in self.data["servers"]:
            raise ValueError(f"Server {server_id} not found")
        
        server = self.data["servers"][server_id]
        total_disk = sum(disk.get("size_gb", 0) for disk in server.get("disks", []))
        
        # Calculate used space by tables (Virtual calculation: 1 record = 1KB for simulation)
        used_space_kb = 0
        for table in server.get("tables", {}).values():
            used_space_kb += len(table.get("records", []))
        
        return {
            "server_id": server_id,
            "cpu_cores": server["cpu"],
            "memory_gb": server["memory_gb"],
            "total_disk_gb": total_disk,
            "data_usage_kb": used_space_kb,
            "table_count": len(server.get("tables", {})),
            "disks": server.get("disks", [])
        }

    def expand_capacity(self, server_id: str, expansion_type: str, amount: int) -> Dict:
        if server_id not in self.data["servers"]:
            raise ValueError(f"Server {server_id} not found")
        
        server = self.data["servers"][server_id]
        
        if expansion_type == "cpu":
            server["cpu"] += amount
        elif expansion_type == "memory":
            server["memory_gb"] += amount
        elif expansion_type == "disk":
            if server.get("disks"):
                largest = max(server["disks"], key=lambda d: d.get("size_gb", 0))
                largest["size_gb"] += amount
        
        self.save_config()
        return {"server_id": server_id, "type": expansion_type, "added": amount}

    def install_disk(self, server_id: str, disk_specs: Dict) -> Dict:
        if server_id not in self.data["servers"]:
            raise ValueError(f"Server {server_id} not found")
        
        server = self.data["servers"][server_id]
        if "disks" not in server: server["disks"] = []
        
        disk_id = f"disk-{len(server['disks']) + 1}"
        new_disk = {
            "id": disk_specs.get("id", disk_id),
            "size_gb": disk_specs.get("size_gb", 100),
            "type": disk_specs.get("type", "SSD"),
            "mount_point": disk_specs.get("mount_point", f"/mnt/{disk_id}"),
            "installed_at": datetime.now().isoformat()
        }
        server["disks"].append(new_disk)
        self.save_config()
        return {"server_id": server_id, "disk": new_disk}

    def add_disk(self, server_id: str, disk_specs: Dict) -> Dict:
        return self.install_disk(server_id, disk_specs)

    # =========================================================
    # New Feature 1: Bulk Customer Registration (가상 고객 대량 반영)
    # =========================================================
    def bulk_register_customers(self, customer_names: List[str]) -> Dict:
        """
        Registers multiple virtual customers at once.
        """
        added_count = 0
        current_ids = {c["id"] for c in self.data["customers"]}
        
        for name in customer_names:
            # Generate a simple unique ID
            cust_id = f"cust-{uuid.uuid4().hex[:8]}"
            
            new_customer = {
                "id": cust_id,
                "name": name.strip(),
                "registered_at": datetime.now().isoformat(),
                "status": "active"
            }
            self.data["customers"].append(new_customer)
            added_count += 1
            
        self.save_config()
        return {
            "status": "success",
            "added_count": added_count,
            "total_customers": len(self.data["customers"])
        }

    # =========================================================
    # New Feature 2: Bulk Table Creation (테이블 대량 생성)
    # =========================================================
    def bulk_create_tables(self, server_id: str, table_names: List[str]) -> Dict:
        """
        Creates multiple data tables in a specific server.
        """
        if server_id not in self.data["servers"]:
            raise ValueError(f"Server {server_id} not found")
        
        server = self.data["servers"][server_id]
        if "tables" not in server:
            server["tables"] = {}
            
        created_tables = []
        
        for table_name in table_names:
            t_name = table_name.strip()
            if t_name in server["tables"]:
                continue # Skip if exists
            
            server["tables"][t_name] = {
                "name": t_name,
                "created_at": datetime.now().isoformat(),
                "records": [],
                "schema": "dynamic" 
            }
            created_tables.append(t_name)
            
        self.save_config()
        return {
            "server_id": server_id,
            "created_count": len(created_tables),
            "tables": created_tables
        }

    # =========================================================
    # New Feature 3: Load Data (적재 기능)
    # =========================================================
    def load_data_records(self, server_id: str, table_name: str, records: List[Dict]) -> Dict:
        """
        Loads (inserts) data records into a specific table on a server.
        """
        if server_id not in self.data["servers"]:
            raise ValueError(f"Server {server_id} not found")
        
        server = self.data["servers"][server_id]
        
        # Auto-create table if it doesn't exist
        if "tables" not in server:
            server["tables"] = {}
        if table_name not in server["tables"]:
            server["tables"][table_name] = {
                "name": table_name,
                "created_at": datetime.now().isoformat(),
                "records": []
            }
            
        table = server["tables"][table_name]
        
        # Load data
        timestamp = datetime.now().isoformat()
        for record in records:
            # Add metadata
            record["_loaded_at"] = timestamp
            table["records"].append(record)
            
        self.save_config()
        return {
            "server_id": server_id,
            "table_name": table_name,
            "loaded_count": len(records),
            "total_records": len(table["records"])
        }
        
    def list_all(self) -> Dict:
        return self.data

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Server Management System v2.0")
    subparsers = parser.add_subparsers(dest="action", help="Action to perform")

    # Existing Commands
    add_parser = subparsers.add_parser("add", help="Add a server")
    add_parser.add_argument("--server-id", required=True)
    add_parser.add_argument("--cpu", type=int)
    add_parser.add_argument("--memory", type=int)

    list_parser = subparsers.add_parser("list", help="List all data")

    # New Features Commands
    
    # 1. Bulk Add Customers
    cust_parser = subparsers.add_parser("bulk-customers", help="Bulk add virtual customers")
    cust_parser.add_argument("--names", required=True, help="Comma separated names (e.g., 'Alice,Bob,Charlie')")

    # 2. Bulk Create Tables
    table_parser = subparsers.add_parser("bulk-tables", help="Bulk create tables")
    table_parser.add_argument("--server-id", required=True)
    table_parser.add_argument("--tables", required=True, help="Comma separated table names (e.g., 'users,orders,logs')")

    # 3. Load Data (적재)
    load_parser = subparsers.add_parser("load-data", help="Load data into a table")
    load_parser.add_argument("--server-id", required=True)
    load_parser.add_argument("--table-name", required=True)
    load_parser.add_argument("--data", required=True, help="JSON string of list or single dict (e.g., '[{\"id\":1}, {\"id\":2}]')")

    args = parser.parse_args()
    manager = ServerManager()
    
    try:
        if args.action == "add":
            specs = {"cpu": args.cpu or 2, "memory_gb": args.memory or 4}
            print(json.dumps(manager.add_server(args.server_id, specs), indent=2))
            
        elif args.action == "list":
            print(json.dumps(manager.list_all(), indent=2, ensure_ascii=False))
            
        elif args.action == "bulk-customers":
            # "홍길동,김철수,이영희" -> ["홍길동", "김철수", "이영희"]
            names = [n.strip() for n in args.names.split(",") if n.strip()]
            result = manager.bulk_register_customers(names)
            print(f"Customer Bulk Load: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
        elif args.action == "bulk-tables":
            # "users,products" -> ["users", "products"]
            tables = [t.strip() for t in args.tables.split(",") if t.strip()]
            result = manager.bulk_create_tables(args.server_id, tables)
            print(f"Table Bulk Create: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
        elif args.action == "load-data":
            # JSON string parsing for data
            try:
                data_payload = json.loads(args.data)
                if isinstance(data_payload, dict):
                    data_payload = [data_payload] # Convert single dict to list
            except json.JSONDecodeError:
                print("Error: --data must be valid JSON string")
                return

            result = manager.load_data_records(args.server_id, args.table_name, data_payload)
            print(f"Data Load Result: {json.dumps(result, indent=2, ensure_ascii=False)}")

        else:
            parser.print_help()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
