#!/usr/bin/env python3
"""
Tests for firewall features in ServerManager
"""

import unittest
import json
import os
import tempfile
from server_manager import ServerManager


class TestFirewallFeatures(unittest.TestCase):
    """Test cases for firewall management features"""
    
    def setUp(self):
        """Create a temporary config file for testing"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.manager = ServerManager(config_file=self.temp_file.name)
        
        # Add a test server
        self.manager.add_server("test-server-1", {
            "cpu": 4,
            "memory_gb": 8,
            "os": "Linux"
        })
    
    def tearDown(self):
        """Clean up temporary file"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_install_firewall_ufw(self):
        """Test installing UFW firewall"""
        result = self.manager.install_firewall("test-server-1", "ufw")
        
        self.assertEqual(result["server_id"], "test-server-1")
        self.assertTrue(result["firewall"]["installed"])
        self.assertEqual(result["firewall"]["type"], "ufw")
        self.assertTrue(result["firewall"]["enabled"])
        self.assertEqual(result["default_rules_added"], 3)
        self.assertGreaterEqual(result["total_rules"], 3)
    
    def test_install_firewall_windows(self):
        """Test installing Windows firewall"""
        self.manager.add_server("test-server-2", {
            "cpu": 4,
            "memory_gb": 8,
            "os": "Windows"
        })
        
        result = self.manager.install_firewall("test-server-2", "windows")
        
        self.assertEqual(result["server_id"], "test-server-2")
        self.assertTrue(result["firewall"]["installed"])
        self.assertEqual(result["firewall"]["type"], "windows")
        self.assertEqual(result["default_rules_added"], 3)
    
    def test_install_firewall_nonexistent_server(self):
        """Test installing firewall on non-existent server"""
        with self.assertRaises(ValueError):
            self.manager.install_firewall("nonexistent-server", "ufw")
    
    def test_add_firewall_rule(self):
        """Test adding a firewall rule"""
        self.manager.install_firewall("test-server-1", "ufw")
        
        rule = {
            "name": "Custom SSH",
            "protocol": "TCP",
            "port": 2222,
            "direction": "inbound",
            "action": "allow"
        }
        
        result = self.manager.add_firewall_rule("test-server-1", rule)
        
        self.assertEqual(result["server_id"], "test-server-1")
        self.assertEqual(result["rule"]["name"], "Custom SSH")
        self.assertEqual(result["rule"]["port"], 2222)
        self.assertEqual(result["rule"]["protocol"], "TCP")
        self.assertGreaterEqual(result["total_rules"], 4)
    
    def test_list_firewall_rules(self):
        """Test listing firewall rules"""
        self.manager.install_firewall("test-server-1", "ufw")
        
        rules = self.manager.list_firewall_rules("test-server-1")
        
        self.assertIsInstance(rules, list)
        self.assertGreaterEqual(len(rules), 3)
        self.assertTrue(any(r["name"] == "SSH" for r in rules))
        self.assertTrue(any(r["name"] == "HTTP" for r in rules))
        self.assertTrue(any(r["name"] == "HTTPS" for r in rules))
    
    def test_remove_firewall_rule(self):
        """Test removing a firewall rule"""
        self.manager.install_firewall("test-server-1", "ufw")
        rules = self.manager.list_firewall_rules("test-server-1")
        
        rule_to_remove = rules[0]["id"]
        result = self.manager.remove_firewall_rule("test-server-1", rule_to_remove)
        
        self.assertTrue(result["removed"])
        self.assertEqual(result["server_id"], "test-server-1")
        self.assertEqual(result["rule_id"], rule_to_remove)
        
        # Verify rule was removed
        updated_rules = self.manager.list_firewall_rules("test-server-1")
        self.assertLess(len(updated_rules), len(rules))
    
    def test_remove_nonexistent_rule(self):
        """Test removing a non-existent rule"""
        self.manager.install_firewall("test-server-1", "ufw")
        
        with self.assertRaises(ValueError):
            self.manager.remove_firewall_rule("test-server-1", "nonexistent-rule-id")
    
    def test_upgrade_firewall(self):
        """Test upgrading firewall with advanced features"""
        self.manager.install_firewall("test-server-1", "ufw")
        
        upgrade_config = {
            "enable_ddos_protection": True,
            "enable_intrusion_detection": True,
            "enable_rate_limiting": True,
            "max_connections": 200
        }
        
        result = self.manager.upgrade_firewall("test-server-1", upgrade_config)
        
        self.assertEqual(result["server_id"], "test-server-1")
        self.assertTrue(result["firewall_config"]["ddos_protection"])
        self.assertTrue(result["firewall_config"]["intrusion_detection"])
        self.assertTrue(result["firewall_config"]["rate_limiting"]["enabled"])
        self.assertEqual(result["firewall_config"]["rate_limiting"]["max_connections"], 200)
        self.assertEqual(len(result["upgrade_info"]["upgrades"]), 3)
    
    def test_upgrade_firewall_without_installation(self):
        """Test upgrading firewall that's not installed"""
        with self.assertRaises(ValueError):
            self.manager.upgrade_firewall("test-server-1", {
                "enable_ddos_protection": True
            })
    
    def test_firewall_rule_persistence(self):
        """Test that firewall rules persist after saving and loading"""
        self.manager.install_firewall("test-server-1", "ufw")
        
        rule = {
            "name": "Custom MySQL",
            "protocol": "TCP",
            "port": 3306,
            "direction": "inbound",
            "action": "allow"
        }
        self.manager.add_firewall_rule("test-server-1", rule)
        
        # Create new manager instance to test persistence
        new_manager = ServerManager(config_file=self.temp_file.name)
        rules = new_manager.list_firewall_rules("test-server-1")
        
        self.assertTrue(any(r["name"] == "Custom MySQL" for r in rules))
        self.assertTrue(any(r["port"] == 3306 for r in rules))
    
    def test_firewall_config_in_server_info(self):
        """Test that firewall config is included in server info"""
        self.manager.install_firewall("test-server-1", "ufw")
        
        server_info = self.manager.get_server_info("test-server-1")
        
        self.assertIn("firewall", server_info)
        self.assertTrue(server_info["firewall"]["installed"])
        self.assertEqual(server_info["firewall"]["type"], "ufw")


if __name__ == "__main__":
    # Run tests
    unittest.main()
