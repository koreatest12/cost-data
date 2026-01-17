package com.costdata.filemanagement.controller;

import com.costdata.filemanagement.config.FirewallConfig;
import com.costdata.filemanagement.dto.ApiResponse;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Controller for firewall management operations
 * Only accessible by ADMIN users
 */
@RestController
@RequestMapping("/api/firewall")
public class FirewallController {
    
    private final FirewallConfig firewallConfig;
    
    public FirewallController(FirewallConfig firewallConfig) {
        this.firewallConfig = firewallConfig;
    }
    
    /**
     * Get current firewall status
     */
    @GetMapping("/status")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<ApiResponse> getStatus() {
        Map<String, Object> status = new HashMap<>();
        status.put("enabled", firewallConfig.isEnabled());
        status.put("whitelist_count", firewallConfig.getWhitelist().size());
        status.put("blacklist_count", firewallConfig.getBlacklist().size());
        status.put("allow_localhost", firewallConfig.isAllowLocalhost());
        status.put("max_requests_per_minute", firewallConfig.getMaxRequestsPerMinute());
        
        return ResponseEntity.ok(ApiResponse.success("Firewall status retrieved", status));
    }
    
    /**
     * Get whitelist IPs
     */
    @GetMapping("/whitelist")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<ApiResponse> getWhitelist() {
        return ResponseEntity.ok(ApiResponse.success("Whitelist retrieved", firewallConfig.getWhitelist()));
    }
    
    /**
     * Add IP to whitelist
     */
    @PostMapping("/whitelist")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<ApiResponse> addToWhitelist(@RequestParam String ip) {
        if (!firewallConfig.getWhitelist().contains(ip)) {
            firewallConfig.getWhitelist().add(ip);
            return ResponseEntity.ok(ApiResponse.success("IP added to whitelist", ip));
        }
        return ResponseEntity.ok(ApiResponse.success("IP already in whitelist", ip));
    }
    
    /**
     * Remove IP from whitelist
     */
    @DeleteMapping("/whitelist")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<ApiResponse> removeFromWhitelist(@RequestParam String ip) {
        if (firewallConfig.getWhitelist().remove(ip)) {
            return ResponseEntity.ok(ApiResponse.success("IP removed from whitelist", ip));
        }
        return ResponseEntity.ok(ApiResponse.success("IP not found in whitelist", ip));
    }
    
    /**
     * Get blacklist IPs
     */
    @GetMapping("/blacklist")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<ApiResponse> getBlacklist() {
        return ResponseEntity.ok(ApiResponse.success("Blacklist retrieved", firewallConfig.getBlacklist()));
    }
    
    /**
     * Add IP to blacklist
     */
    @PostMapping("/blacklist")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<ApiResponse> addToBlacklist(@RequestParam String ip) {
        if (!firewallConfig.getBlacklist().contains(ip)) {
            firewallConfig.getBlacklist().add(ip);
            return ResponseEntity.ok(ApiResponse.success("IP added to blacklist", ip));
        }
        return ResponseEntity.ok(ApiResponse.success("IP already in blacklist", ip));
    }
    
    /**
     * Remove IP from blacklist
     */
    @DeleteMapping("/blacklist")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<ApiResponse> removeFromBlacklist(@RequestParam String ip) {
        if (firewallConfig.getBlacklist().remove(ip)) {
            return ResponseEntity.ok(ApiResponse.success("IP removed from blacklist", ip));
        }
        return ResponseEntity.ok(ApiResponse.success("IP not found in blacklist", ip));
    }
    
    /**
     * Enable or disable firewall
     */
    @PostMapping("/toggle")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<ApiResponse> toggleFirewall(@RequestParam boolean enabled) {
        firewallConfig.setEnabled(enabled);
        String message = enabled ? "Firewall enabled" : "Firewall disabled";
        return ResponseEntity.ok(ApiResponse.success(message, enabled));
    }
    
    /**
     * Update rate limit
     */
    @PostMapping("/rate-limit")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<ApiResponse> updateRateLimit(@RequestParam int maxRequestsPerMinute) {
        if (maxRequestsPerMinute < 1) {
            return ResponseEntity.badRequest().body(
                ApiResponse.error("Rate limit must be at least 1")
            );
        }
        firewallConfig.setMaxRequestsPerMinute(maxRequestsPerMinute);
        return ResponseEntity.ok(ApiResponse.success("Rate limit updated", maxRequestsPerMinute));
    }
}
