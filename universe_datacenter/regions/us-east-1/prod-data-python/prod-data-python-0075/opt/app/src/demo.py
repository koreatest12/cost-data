#!/usr/bin/env python3
"""
Example demonstration of all server management features
Run this to see all features in action
"""

from server_manager import ServerManager
import json

def print_section(title):
    """Print a section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_result(data):
    """Print JSON data in a readable format"""
    print(json.dumps(data, indent=2, ensure_ascii=False))

def main():
    # Use a demo config file
    manager = ServerManager(config_file="demo_config.json")
    
    print_section("1. 서버 추가 (Add Server)")
    print("Adding web-server-1 with 2 CPU cores and 4GB RAM...")
    result = manager.add_server("web-server-1", {
        "cpu": 2,
        "memory_gb": 4,
        "os": "Ubuntu 22.04"
    })
    print_result(result)
    
    print_section("2. 용량 체크 (Check Capacity)")
    print("Checking current capacity of web-server-1...")
    capacity = manager.check_capacity("web-server-1")
    print_result(capacity)
    
    print_section("3. 서버 업그레이드 (Server Upgrade)")
    print("Upgrading to 4 CPU cores and 16GB RAM...")
    upgrade = manager.upgrade_server("web-server-1", {
        "cpu": 4,
        "memory_gb": 16
    })
    print_result(upgrade)
    
    print_section("4. 디스크 설치 (Disk Installation)")
    print("Installing a 500GB SSD disk...")
    disk1 = manager.install_disk("web-server-1", {
        "size_gb": 500,
        "type": "SSD"
    })
    print_result(disk1)
    
    print_section("5. 디스크 추가 반영 (Add Disk with Reflection)")
    print("Adding and reflecting a 1000GB HDD disk...")
    disk2 = manager.add_disk("web-server-1", {
        "size_gb": 1000,
        "type": "HDD"
    })
    print_result(disk2)
    
    print_section("6. 용량 증설 - CPU (Expand CPU Capacity)")
    print("Expanding CPU by 2 cores...")
    expand_cpu = manager.expand_capacity("web-server-1", "cpu", 2)
    print_result(expand_cpu)
    
    print_section("7. 용량 증설 - Memory (Expand Memory Capacity)")
    print("Expanding memory by 8GB...")
    expand_mem = manager.expand_capacity("web-server-1", "memory", 8)
    print_result(expand_mem)
    
    print_section("8. 용량 증설 - Disk (Expand Disk Capacity)")
    print("Expanding disk by 200GB...")
    expand_disk = manager.expand_capacity("web-server-1", "disk", 200)
    print_result(expand_disk)
    
    print_section("9. 최종 용량 확인 (Final Capacity Check)")
    print("Checking final capacity after all operations...")
    final_capacity = manager.check_capacity("web-server-1")
    print_result(final_capacity)
    
    print_section("10. 서버 상세 정보 (Server Details)")
    print("Getting complete server information...")
    info = manager.get_server_info("web-server-1")
    print_result(info)
    
    # Add another server
    print_section("11. 추가 서버 생성 (Add Another Server)")
    print("Adding database-server-1 with high specs...")
    db_server = manager.add_server("database-server-1", {
        "cpu": 8,
        "memory_gb": 32,
        "os": "CentOS 8"
    })
    print_result(db_server)
    
    print_section("12. 모든 서버 목록 (List All Servers)")
    print("Listing all servers in the system...")
    all_servers = manager.list_servers()
    print(f"Total servers: {len(all_servers)}")
    for server in all_servers:
        print(f"\n- {server['id']}: {server['cpu']} cores, {server['memory_gb']}GB RAM, {len(server.get('disks', []))} disks")
    
    print_section("Demo Complete!")
    print(f"Configuration saved to: demo_config.json")
    print("\nYou can inspect the configuration file to see how data is stored.")
    print("\nTo clean up the demo, run: rm -f demo_config.json")

if __name__ == "__main__":
    main()
