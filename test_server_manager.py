#!/usr/bin/env python3
"""
Tests for Server Management System
"""

import unittest
import json
import os
import tempfile
from server_manager import ServerManager


class TestServerManager(unittest.TestCase):
    """Test cases for ServerManager class"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_config.close()
        self.manager = ServerManager(config_file=self.temp_config.name)
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_config.name):
            os.unlink(self.temp_config.name)
    
    def test_add_server(self):
        """Test adding a new server"""
        server_id = "test-server-1"
        specs = {
            "cpu": 4,
            "memory_gb": 8,
            "os": "Ubuntu 22.04"
        }
        
        result = self.manager.add_server(server_id, specs)
        
        self.assertEqual(result["id"], server_id)
        self.assertEqual(result["cpu"], 4)
        self.assertEqual(result["memory_gb"], 8)
        self.assertEqual(result["os"], "Ubuntu 22.04")
        self.assertIn(server_id, self.manager.servers)
    
    def test_add_duplicate_server(self):
        """Test adding a duplicate server raises error"""
        server_id = "test-server-1"
        specs = {"cpu": 2, "memory_gb": 4}
        
        self.manager.add_server(server_id, specs)
        
        with self.assertRaises(ValueError) as context:
            self.manager.add_server(server_id, specs)
        
        self.assertIn("already exists", str(context.exception))
    
    def test_upgrade_server_cpu(self):
        """Test server CPU upgrade"""
        server_id = "test-server-2"
        self.manager.add_server(server_id, {"cpu": 2, "memory_gb": 4})
        
        result = self.manager.upgrade_server(server_id, {"cpu": 4})
        
        self.assertEqual(result["current_specs"]["cpu"], 4)
        self.assertEqual(result["upgrade_info"]["changes"]["cpu"]["from"], 2)
        self.assertEqual(result["upgrade_info"]["changes"]["cpu"]["to"], 4)
    
    def test_upgrade_server_memory(self):
        """Test server memory upgrade"""
        server_id = "test-server-3"
        self.manager.add_server(server_id, {"cpu": 2, "memory_gb": 4})
        
        result = self.manager.upgrade_server(server_id, {"memory_gb": 16})
        
        self.assertEqual(result["current_specs"]["memory_gb"], 16)
        self.assertEqual(result["upgrade_info"]["changes"]["memory_gb"]["from"], 4)
        self.assertEqual(result["upgrade_info"]["changes"]["memory_gb"]["to"], 16)
    
    def test_upgrade_server_both_cpu_and_memory(self):
        """Test upgrading both CPU and memory"""
        server_id = "test-server-4"
        self.manager.add_server(server_id, {"cpu": 2, "memory_gb": 4})
        
        result = self.manager.upgrade_server(server_id, {"cpu": 8, "memory_gb": 32})
        
        self.assertEqual(result["current_specs"]["cpu"], 8)
        self.assertEqual(result["current_specs"]["memory_gb"], 32)
        self.assertIn("cpu", result["upgrade_info"]["changes"])
        self.assertIn("memory_gb", result["upgrade_info"]["changes"])
    
    def test_upgrade_nonexistent_server(self):
        """Test upgrading a non-existent server raises error"""
        with self.assertRaises(ValueError) as context:
            self.manager.upgrade_server("nonexistent", {"cpu": 4})
        
        self.assertIn("not found", str(context.exception))
    
    def test_check_capacity(self):
        """Test capacity check feature"""
        server_id = "test-server-5"
        self.manager.add_server(server_id, {"cpu": 4, "memory_gb": 16})
        
        # Add some disks
        self.manager.install_disk(server_id, {"size_gb": 500, "type": "SSD"})
        self.manager.install_disk(server_id, {"size_gb": 1000, "type": "HDD"})
        
        result = self.manager.check_capacity(server_id)
        
        self.assertEqual(result["server_id"], server_id)
        self.assertEqual(result["cpu_cores"], 4)
        self.assertEqual(result["memory_gb"], 16)
        self.assertEqual(result["total_disk_gb"], 1500)
        self.assertEqual(result["disk_count"], 2)
    
    def test_check_capacity_nonexistent_server(self):
        """Test checking capacity of non-existent server"""
        with self.assertRaises(ValueError) as context:
            self.manager.check_capacity("nonexistent")
        
        self.assertIn("not found", str(context.exception))
    
    def test_expand_capacity_cpu(self):
        """Test CPU capacity expansion"""
        server_id = "test-server-6"
        self.manager.add_server(server_id, {"cpu": 2, "memory_gb": 4})
        
        result = self.manager.expand_capacity(server_id, "cpu", 2)
        
        self.assertEqual(result["type"], "cpu")
        self.assertEqual(result["amount"], 2)
        self.assertEqual(result["old_value"], 2)
        self.assertEqual(result["new_value"], 4)
    
    def test_expand_capacity_memory(self):
        """Test memory capacity expansion"""
        server_id = "test-server-7"
        self.manager.add_server(server_id, {"cpu": 2, "memory_gb": 4})
        
        result = self.manager.expand_capacity(server_id, "memory", 8)
        
        self.assertEqual(result["type"], "memory")
        self.assertEqual(result["amount"], 8)
        self.assertEqual(result["old_value"], 4)
        self.assertEqual(result["new_value"], 12)
    
    def test_expand_capacity_disk(self):
        """Test disk capacity expansion"""
        server_id = "test-server-8"
        self.manager.add_server(server_id, {"cpu": 2, "memory_gb": 4})
        self.manager.install_disk(server_id, {"size_gb": 100, "type": "SSD"})
        
        result = self.manager.expand_capacity(server_id, "disk", 50)
        
        self.assertEqual(result["type"], "disk")
        self.assertEqual(result["amount"], 50)
        self.assertEqual(result["old_value"], 100)
        self.assertEqual(result["new_value"], 150)
    
    def test_install_disk(self):
        """Test disk installation feature"""
        server_id = "test-server-9"
        self.manager.add_server(server_id, {"cpu": 2, "memory_gb": 4})
        
        disk_specs = {
            "size_gb": 500,
            "type": "SSD"
        }
        
        result = self.manager.install_disk(server_id, disk_specs)
        
        self.assertEqual(result["server_id"], server_id)
        self.assertEqual(result["disk"]["size_gb"], 500)
        self.assertEqual(result["disk"]["type"], "SSD")
        self.assertEqual(result["total_disks"], 1)
        
        # Verify disk is in server config
        server = self.manager.get_server_info(server_id)
        self.assertEqual(len(server["disks"]), 1)
        self.assertEqual(server["disks"][0]["size_gb"], 500)
    
    def test_install_multiple_disks(self):
        """Test installing multiple disks"""
        server_id = "test-server-10"
        self.manager.add_server(server_id, {"cpu": 2, "memory_gb": 4})
        
        # Install first disk
        result1 = self.manager.install_disk(server_id, {"size_gb": 100, "type": "SSD"})
        self.assertEqual(result1["total_disks"], 1)
        
        # Install second disk
        result2 = self.manager.install_disk(server_id, {"size_gb": 200, "type": "HDD"})
        self.assertEqual(result2["total_disks"], 2)
        
        # Verify both disks are present
        server = self.manager.get_server_info(server_id)
        self.assertEqual(len(server["disks"]), 2)
    
    def test_add_disk_with_reflection(self):
        """Test disk addition with reflection feature"""
        server_id = "test-server-11"
        self.manager.add_server(server_id, {"cpu": 2, "memory_gb": 4})
        
        disk_specs = {
            "size_gb": 1000,
            "type": "SSD"
        }
        
        result = self.manager.add_disk(server_id, disk_specs)
        
        self.assertEqual(result["server_id"], server_id)
        self.assertEqual(result["disk"]["size_gb"], 1000)
        self.assertTrue(result["reflected"])
        self.assertIn("reflection_timestamp", result)
    
    def test_get_server_info(self):
        """Test getting server information"""
        server_id = "test-server-12"
        specs = {"cpu": 4, "memory_gb": 16, "os": "CentOS 8"}
        self.manager.add_server(server_id, specs)
        
        info = self.manager.get_server_info(server_id)
        
        self.assertEqual(info["id"], server_id)
        self.assertEqual(info["cpu"], 4)
        self.assertEqual(info["memory_gb"], 16)
        self.assertEqual(info["os"], "CentOS 8")
    
    def test_list_servers(self):
        """Test listing all servers"""
        self.manager.add_server("server-1", {"cpu": 2, "memory_gb": 4})
        self.manager.add_server("server-2", {"cpu": 4, "memory_gb": 8})
        self.manager.add_server("server-3", {"cpu": 8, "memory_gb": 16})
        
        servers = self.manager.list_servers()
        
        self.assertEqual(len(servers), 3)
        server_ids = [s["id"] for s in servers]
        self.assertIn("server-1", server_ids)
        self.assertIn("server-2", server_ids)
        self.assertIn("server-3", server_ids)
    
    def test_upgrade_history(self):
        """Test that upgrades are recorded in history"""
        server_id = "test-server-13"
        self.manager.add_server(server_id, {"cpu": 2, "memory_gb": 4})
        
        # Perform multiple upgrades
        self.manager.upgrade_server(server_id, {"cpu": 4})
        self.manager.upgrade_server(server_id, {"memory_gb": 8})
        
        server = self.manager.get_server_info(server_id)
        
        self.assertEqual(len(server["upgrade_history"]), 2)
        self.assertIn("timestamp", server["upgrade_history"][0])
    
    def test_disk_history(self):
        """Test that disk installations are recorded in history"""
        server_id = "test-server-14"
        self.manager.add_server(server_id, {"cpu": 2, "memory_gb": 4})
        
        # Install disks
        self.manager.install_disk(server_id, {"size_gb": 100, "type": "SSD"})
        self.manager.install_disk(server_id, {"size_gb": 200, "type": "HDD"})
        
        server = self.manager.get_server_info(server_id)
        
        self.assertEqual(len(server["disk_history"]), 2)
        self.assertEqual(server["disk_history"][0]["action"], "install")
    
    def test_persistence(self):
        """Test that configuration is persisted to file"""
        server_id = "test-server-15"
        self.manager.add_server(server_id, {"cpu": 2, "memory_gb": 4})
        
        # Create a new manager instance with the same config file
        manager2 = ServerManager(config_file=self.temp_config.name)
        
        # Verify server was loaded from file
        self.assertIn(server_id, manager2.servers)
        self.assertEqual(manager2.servers[server_id]["cpu"], 2)


if __name__ == "__main__":
    unittest.main()
