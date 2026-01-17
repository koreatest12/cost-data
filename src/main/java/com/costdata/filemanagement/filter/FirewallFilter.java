package com.costdata.filemanagement.filter;

import com.costdata.filemanagement.config.FirewallConfig;
import jakarta.servlet.*;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Firewall filter for IP-based access control and rate limiting
 */
@Component
public class FirewallFilter implements Filter {
    
    private static final Logger logger = LoggerFactory.getLogger(FirewallFilter.class);
    
    private final FirewallConfig firewallConfig;
    private final Map<String, AtomicInteger> requestCounts = new ConcurrentHashMap<>();
    private long lastResetTime = System.currentTimeMillis();
    
    public FirewallFilter(FirewallConfig firewallConfig) {
        this.firewallConfig = firewallConfig;
    }
    
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) 
            throws IOException, ServletException {
        
        HttpServletRequest httpRequest = (HttpServletRequest) request;
        HttpServletResponse httpResponse = (HttpServletResponse) response;
        
        String ipAddress = getClientIpAddress(httpRequest);
        
        // IP-based firewall check - perform early to prevent information leakage
        if (!firewallConfig.isIpAllowed(ipAddress)) {
            logger.warn("Firewall blocked request from IP: {}", ipAddress);
            httpResponse.setStatus(HttpServletResponse.SC_FORBIDDEN);
            httpResponse.setContentType("application/json");
            httpResponse.getWriter().write("{\"error\":\"Access denied\"}");
            return;
        }
        
        // Rate limiting check
        if (!checkRateLimit(ipAddress)) {
            logger.warn("Rate limit exceeded for IP: {}", ipAddress);
            httpResponse.setStatus(429); // Too Many Requests
            httpResponse.setContentType("application/json");
            httpResponse.getWriter().write("{\"error\":\"Too many requests\"}");
            return;
        }
        
        chain.doFilter(request, response);
    }
    
    private String getClientIpAddress(HttpServletRequest request) {
        String xForwardedFor = request.getHeader("X-Forwarded-For");
        if (xForwardedFor != null && !xForwardedFor.isEmpty()) {
            return xForwardedFor.split(",")[0].trim();
        }
        
        String xRealIp = request.getHeader("X-Real-IP");
        if (xRealIp != null && !xRealIp.isEmpty()) {
            return xRealIp;
        }
        
        return request.getRemoteAddr();
    }
    
    private boolean checkRateLimit(String ipAddress) {
        // Reset counters every minute with synchronized access to prevent race conditions
        long currentTime = System.currentTimeMillis();
        synchronized (this) {
            if (currentTime - lastResetTime > 60000) {
                requestCounts.clear();
                lastResetTime = currentTime;
            }
        }
        
        AtomicInteger count = requestCounts.computeIfAbsent(ipAddress, k -> new AtomicInteger(0));
        int currentCount = count.incrementAndGet();
        
        return currentCount <= firewallConfig.getMaxRequestsPerMinute();
    }
}
