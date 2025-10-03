#!/bin/bash
# Persistent URL Manager - Maintains consistent external URL
# Uses Cloudflare Named Tunnels for persistent URLs

echo "🌐 Persistent URL Manager"
echo "========================"

TUNNEL_NAME="rag-api-tunnel"
TUNNEL_CONFIG_FILE="tunnel-config.yml"
TUNNEL_CREDENTIALS_FILE="tunnel-credentials.json"

# Function to create named tunnel
create_named_tunnel() {
    echo "🔧 Creating named tunnel: $TUNNEL_NAME"
    
    # Create tunnel credentials
    ./cloudflared tunnel create $TUNNEL_NAME > $TUNNEL_CREDENTIALS_FILE
    
    # Create tunnel configuration
    cat > $TUNNEL_CONFIG_FILE << EOF
tunnel: $TUNNEL_NAME
credentials-file: $TUNNEL_CREDENTIALS_FILE

ingress:
  - hostname: rag-api.your-domain.com
    service: http://umd-cscdr-gpu001:8081
  - service: http_status:404
EOF
    
    echo "✅ Named tunnel created: $TUNNEL_NAME"
    echo "📋 Configuration saved to: $TUNNEL_CONFIG_FILE"
}

# Function to start persistent tunnel
start_persistent_tunnel() {
    echo "🌐 Starting persistent tunnel..."
    
    if [ ! -f "$TUNNEL_CONFIG_FILE" ]; then
        echo "❌ Tunnel configuration not found. Creating..."
        create_named_tunnel
    fi
    
    # Start tunnel with configuration
    nohup ./cloudflared tunnel --config $TUNNEL_CONFIG_FILE run $TUNNEL_NAME > tunnel.log 2>&1 &
    echo $! > tunnel.pid
    
    echo "✅ Persistent tunnel started (PID: $(cat tunnel.pid))"
    echo "🌐 Your persistent URL: https://rag-api.your-domain.com"
    echo "📋 This URL will remain the same across restarts"
}

# Function to stop tunnel
stop_tunnel() {
    if [ -f "tunnel.pid" ]; then
        local pid=$(cat tunnel.pid)
        kill $pid 2>/dev/null
        rm tunnel.pid
        echo "✅ Tunnel stopped"
    fi
}

# Function to get tunnel status
get_status() {
    echo "📊 Persistent Tunnel Status"
    echo "=========================="
    
    if [ -f "tunnel.pid" ]; then
        local pid=$(cat tunnel.pid)
        if kill -0 $pid 2>/dev/null; then
            echo "✅ Tunnel running (PID: $pid)"
            echo "🌐 Persistent URL: https://rag-api.your-domain.com"
        else
            echo "❌ Tunnel not running"
        fi
    else
        echo "❌ Tunnel not started"
    fi
    
    # Check RAG API job
    local job_id=$(squeue -u $USER --format="%.18i %.9P %.20j %.8u %.8T %.10M %.6D %R" | grep "rag_api_" | head -1 | awk '{print $1}')
    if [ -n "$job_id" ]; then
        echo "✅ RAG API job running: $job_id"
    else
        echo "❌ No RAG API job found"
    fi
}

# Function to monitor and maintain tunnel
monitor_tunnel() {
    echo "🔍 Starting persistent tunnel monitor..."
    echo "📡 This will maintain a consistent tunnel URL"
    echo "🔄 Tunnel will restart if job changes"
    echo ""
    
    local current_job=$(squeue -u $USER --format="%.18i %.9P %.20j %.8u %.8T %.10M %.6D %R" | grep "rag_api_" | head -1 | awk '{print $1}')
    if [ -z "$current_job" ]; then
        echo "❌ No RAG API job found. Please start the API first:"
        echo "   ./manage_rag_hosting.sh start"
        return 1
    fi
    
    echo "✅ Found RAG API job: $current_job"
    echo $current_job > last_job.txt
    
    # Start initial tunnel
    start_persistent_tunnel
    
    # Wait for tunnel to establish
    echo "⏳ Waiting for tunnel to establish..."
    sleep 10
    
    echo ""
    echo "🔄 Monitoring for job changes..."
    echo "Press Ctrl+C to stop monitoring"
    
    # Monitor loop
    while true; do
        local new_job=$(squeue -u $USER --format="%.18i %.9P %.20j %.8u %.8T %.10M %.6D %R" | grep "rag_api_" | head -1 | awk '{print $1}')
        local last_job=$(cat last_job.txt 2>/dev/null)
        
        if [ "$new_job" != "$last_job" ] && [ -n "$new_job" ]; then
            echo "🔄 Job changed: $last_job → $new_job"
            echo "🔄 Restarting tunnel..."
            
            stop_tunnel
            sleep 2
            start_persistent_tunnel
            sleep 10
            
            echo "🌐 Persistent URL maintained: https://rag-api.your-domain.com"
            echo $new_job > last_job.txt
        fi
        
        sleep 30  # Check every 30 seconds
    done
}

# Main command handling
case "${1:-help}" in
    "start")
        start_persistent_tunnel
        ;;
    "monitor")
        monitor_tunnel
        ;;
    "stop")
        stop_tunnel
        ;;
    "status")
        get_status
        ;;
    "create")
        create_named_tunnel
        ;;
    *)
        echo "Usage: $0 {start|monitor|stop|status|create}"
        echo ""
        echo "Commands:"
        echo "  start   - Start persistent tunnel"
        echo "  monitor - Start monitoring with auto-restart"
        echo "  stop    - Stop tunnel"
        echo "  status  - Check tunnel status"
        echo "  create  - Create new named tunnel"
        echo ""
        echo "🎯 Benefits:"
        echo "  • Maintains same URL across restarts"
        echo "  • Uses Cloudflare Named Tunnels"
        echo "  • Professional persistent URLs"
        echo "  • No random URL changes"
        exit 1
        ;;
esac

