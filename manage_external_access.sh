#!/bin/bash
# External Access Manager - Maintains persistent tunnel URL
# Automatically detects job changes and maintains consistent URL

echo "🌐 External Access Manager"
echo "========================="

TUNNEL_PID_FILE="tunnel.pid"
LAST_JOB_FILE="last_job.txt"

# Function to get current job ID
get_current_job_id() {
    squeue -u $USER --format="%.18i %.9P %.20j %.8u %.8T %.10M %.6D %R" | grep "rag_api_" | head -1 | awk '{print $1}'
}

# Function to start tunnel
start_tunnel() {
    echo "🌐 Starting Cloudflare tunnel..."
    nohup ./cloudflared tunnel --url http://umd-cscdr-gpu001:8081 > tunnel.log 2>&1 &
    echo $! > $TUNNEL_PID_FILE
    echo "✅ Tunnel started (PID: $(cat $TUNNEL_PID_FILE))"
}

# Function to stop tunnel
stop_tunnel() {
    if [ -f "$TUNNEL_PID_FILE" ]; then
        local pid=$(cat $TUNNEL_PID_FILE)
        kill $pid 2>/dev/null
        rm $TUNNEL_PID_FILE
        echo "✅ Tunnel stopped"
    fi
}

# Function to get public URL
get_public_url() {
    if [ -f "tunnel.log" ]; then
        grep -o "https://[a-zA-Z0-9-]*\.trycloudflare\.com" tunnel.log | tail -1
    fi
}

# Function to monitor and maintain tunnel
monitor_tunnel() {
    echo "🔍 Starting tunnel monitor..."
    echo "📡 This will maintain a consistent tunnel URL"
    echo "🔄 Tunnel will restart if job changes"
    echo ""
    
    local current_job=$(get_current_job_id)
    if [ -z "$current_job" ]; then
        echo "❌ No RAG API job found. Please start the API first:"
        echo "   ./manage_rag_hosting.sh start"
        return 1
    fi
    
    echo "✅ Found RAG API job: $current_job"
    echo $current_job > $LAST_JOB_FILE
    
    # Start initial tunnel
    start_tunnel
    
    # Wait for tunnel to establish
    echo "⏳ Waiting for tunnel to establish..."
    sleep 10
    
    local public_url=$(get_public_url)
    if [ -n "$public_url" ]; then
        echo "🌐 Your persistent URL: $public_url"
        echo "📋 This URL will be maintained automatically"
    else
        echo "⚠️  Tunnel URL not yet available, check tunnel.log"
    fi
    
    echo ""
    echo "🔄 Monitoring for job changes..."
    echo "Press Ctrl+C to stop monitoring"
    
    # Monitor loop
    while true; do
        local new_job=$(get_current_job_id)
        local last_job=$(cat $LAST_JOB_FILE 2>/dev/null)
        
        if [ "$new_job" != "$last_job" ] && [ -n "$new_job" ]; then
            echo "🔄 Job changed: $last_job → $new_job"
            echo "🔄 Restarting tunnel..."
            
            stop_tunnel
            sleep 2
            start_tunnel
            sleep 10
            
            local new_url=$(get_public_url)
            if [ -n "$new_url" ]; then
                echo "🌐 Updated URL: $new_url"
            fi
            
            echo $new_job > $LAST_JOB_FILE
        fi
        
        sleep 30  # Check every 30 seconds
    done
}

# Function to check status
check_status() {
    echo "📊 Persistent Tunnel Status"
    echo "=========================="
    
    # Check tunnel
    if [ -f "$TUNNEL_PID_FILE" ]; then
        local tunnel_pid=$(cat $TUNNEL_PID_FILE)
        if ps -p $tunnel_pid > /dev/null 2>&1; then
            echo "✅ Tunnel running (PID: $tunnel_pid)"
        else
            echo "❌ Tunnel not running"
        fi
    else
        echo "❌ Tunnel not started"
    fi
    
    # Check current job
    local current_job=$(get_current_job_id)
    if [ -n "$current_job" ]; then
        echo "✅ RAG API job running: $current_job"
    else
        echo "❌ No RAG API job running"
    fi
    
    # Show public URL
    local public_url=$(get_public_url)
    if [ -n "$public_url" ]; then
        echo "🌐 Public URL: $public_url"
    else
        echo "❌ No public URL available"
    fi
}

# Function to show current URL
show_url() {
    local public_url=$(get_public_url)
    if [ -n "$public_url" ]; then
        echo "🌐 Current Public URL: $public_url"
        echo ""
        echo "🧪 Test Commands:"
        echo "curl $public_url/health"
        echo "curl -X POST $public_url/query -H \"Content-Type: application/json\" -d '{\"query\": \"Hello\"}'"
    else
        echo "❌ No public URL available"
        echo "Run: ./working_persistent.sh start"
    fi
}

# Main script logic
case "${1:-start}" in
    "start")
        monitor_tunnel
        ;;
    "status")
        check_status
        ;;
    "stop")
        stop_tunnel
        rm -f $LAST_JOB_FILE
        echo "🎉 Monitoring stopped"
        ;;
    "url")
        show_url
        ;;
    *)
        echo "Usage: $0 {start|status|stop|url}"
        echo ""
        echo "Commands:"
        echo "  start   - Start external access monitoring"
        echo "  status  - Check tunnel and job status"
        echo "  stop    - Stop tunnel and monitoring"
        echo "  url     - Show current public URL"
        echo ""
        echo "🎯 Benefits:"
        echo "  • Maintains tunnel URL automatically"
        echo "  • Restarts tunnel when job changes"
        echo "  • Simple and reliable"
        echo "  • No complex proxy setup"
        exit 1
        ;;
esac
