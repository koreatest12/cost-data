package com.costdata.filemanagement.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;
import java.util.ArrayList;
import java.util.List;

/**
 * Firewall configuration for IP-based access control
 * Supports whitelist and blacklist IP filtering
 */
@Configuration
@ConfigurationProperties(prefix = "firewall")
public class FirewallConfig {
    
    private boolean enabled = true;
    private List<String> whitelist = new ArrayList<>();
    private List<String> blacklist = new ArrayList<>();
    private boolean allowLocalhost = true;
    private int maxRequestsPerMinute = 100;
    
    public boolean isEnabled() {
        return enabled;
    }
    
    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }
    
    public List<String> getWhitelist() {
        return whitelist;
    }
    
    public void setWhitelist(List<String> whitelist) {
        this.whitelist = whitelist;
    }
    
    public List<String> getBlacklist() {
        return blacklist;
    }
    
    public void setBlacklist(List<String> blacklist) {
        this.blacklist = blacklist;
    }
    
    public boolean isAllowLocalhost() {
        return allowLocalhost;
    }
    
    public void setAllowLocalhost(boolean allowLocalhost) {
        this.allowLocalhost = allowLocalhost;
    }
    
    public int getMaxRequestsPerMinute() {
        return maxRequestsPerMinute;
    }
    
    public void setMaxRequestsPerMinute(int maxRequestsPerMinute) {
        this.maxRequestsPerMinute = maxRequestsPerMinute;
    }
    
    public boolean isIpAllowed(String ipAddress) {
        if (!enabled) {
            return true;
        }
        
        // Check if localhost is allowed
        if (allowLocalhost && isLocalhost(ipAddress)) {
            return true;
        }
        
        // Check blacklist first
        if (!blacklist.isEmpty() && blacklist.contains(ipAddress)) {
            return false;
        }
        
        // If whitelist is configured, only allow whitelisted IPs
        if (!whitelist.isEmpty()) {
            return whitelist.contains(ipAddress);
        }
        
        // If no whitelist is configured, allow all IPs not in blacklist
        return true;
    }
    
    private boolean isLocalhost(String ipAddress) {
        return "127.0.0.1".equals(ipAddress) || 
               "0:0:0:0:0:0:0:1".equals(ipAddress) || 
               "::1".equals(ipAddress) ||
               "localhost".equalsIgnoreCase(ipAddress);
    }
}
