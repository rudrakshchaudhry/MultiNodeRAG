#!/bin/bash

# External Access Management Script for RAG API
# This script manages Cloudflare Tunnel for external access

TUNNEL_PID_FILE="tunnel.pid"
TUNNEL_LOG_FILE="tunnel.log"

# Function to get current job ID
get_current_job_id() {
    squeue -u $USER --noheader --format="%.i" | grep "rag_api" | head -1
}

# Function to get current node from running job
get_current_node() {
    local job_id=$(get_current_job_id)
    if [ -z "$job_id" ]; then
        return 1
    fi
    
    # Get the node from squeue output
    local node=$(squeue -j $job_id --noheader --format="%.N" 2>/dev/null | head -1)
    if [ -n "$node" ]; then
        echo "$node"
    else
        # Fallback: try to get from job info
        local node=$(scontrol show job $job_id 2>/dev/null | grep "NodeList" | cut -d'=' -f2 | cut -d',' -f1)
        echo "$node"
    fi
}

# Function to start tunnel
start_tunnel() {
    local node=$(get_current_node)
    if [ -z "$node" ]; then
        echo "❌ Could not determine current node"
        return 1
    fi
    
    echo "🌐 Starting Cloudflare tunnel..."
    echo "📡 Connecting to: $node:8081"
    nohup ./cloudflared tunnel --url http://$node:8081 > $TUNNEL_LOG_FILE 2>&1 &
    echo $! > $TUNNEL_PID_FILE
    echo "✅ Tunnel started (PID: $(cat $TUNNEL_PID_FILE))"
    
    # Wait for tunnel to establish
    sleep 5
    
    # Extract URL from log
    local url=$(grep -E "https://.*\.trycloudflare\.com" $TUNNEL_LOG_FILE | tail -1 | sed 's/.*|  \(https:\/\/[^ ]*\) .*/\1/')
    if [ -n "$url" ]; then
        echo "🔗 External URL: $url"
    fi
}

# Function to stop tunnel
stop_tunnel() {
    if [ -f "$TUNNEL_PID_FILE" ]; then
        local pid=$(cat $TUNNEL_PID_FILE)
        if kill -0 $pid 2>/dev/null; then
            echo "🛑 Stopping tunnel (PID: $pid)..."
            kill $pid
            rm -f $TUNNEL_PID_FILE
            echo "✅ Tunnel stopped"
        else
            echo "⚠️  Tunnel process not running"
            rm -f $TUNNEL_PID_FILE
        fi
    else
        echo "⚠️  No tunnel PID file found"
    fi
}

# Function to check tunnel status
status_tunnel() {
    if [ -f "$TUNNEL_PID_FILE" ]; then
        local pid=$(cat $TUNNEL_PID_FILE)
        if kill -0 $pid 2>/dev/null; then
            echo "✅ Tunnel is running (PID: $pid)"
            
            # Get current URL
            local url=$(grep -E "https://.*\.trycloudflare\.com" $TUNNEL_LOG_FILE | tail -1 | sed 's/.*|  \(https:\/\/[^ ]*\) .*/\1/')
            if [ -n "$url" ]; then
                echo "🔗 External URL: $url"
            fi
            
            # Show recent log entries
            echo "📋 Recent tunnel activity:"
            tail -3 $TUNNEL_LOG_FILE
        else
            echo "❌ Tunnel process not running"
            rm -f $TUNNEL_PID_FILE
        fi
    else
        echo "❌ No tunnel running"
    fi
}

# Function to get current URL
get_url() {
    if [ -f "$TUNNEL_LOG_FILE" ]; then
        local url=$(grep -E "https://.*\.trycloudflare\.com" $TUNNEL_LOG_FILE | tail -1 | sed 's/.*|  \(https:\/\/[^ ]*\) .*/\1/')
        if [ -n "$url" ]; then
            echo "$url"
        else
            echo "❌ No URL found in tunnel log"
        fi
    else
        echo "❌ No tunnel log found"
    fi
}

# Function to restart tunnel
restart_tunnel() {
    echo "🔄 Restarting tunnel..."
    stop_tunnel
    sleep 2
    start_tunnel
}

# Main command handling
case "$1" in
    start)
        start_tunnel
        ;;
    stop)
        stop_tunnel
        ;;
    restart)
        restart_tunnel
        ;;
    status)
        status_tunnel
        ;;
    url)
        get_url
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|url}"
        echo ""
        echo "Commands:"
        echo "  start   - Start Cloudflare tunnel"
        echo "  stop    - Stop Cloudflare tunnel"
        echo "  restart - Restart Cloudflare tunnel"
        echo "  status  - Show tunnel status and URL"
        echo "  url     - Get current external URL"
        exit 1
        ;;
esac
