#!/bin/bash
# URL Tracker - Tracks and reports URL changes
# Provides consistent access despite URL changes

echo "🔗 URL Tracker"
echo "============="

URL_LOG_FILE="url_history.log"
CURRENT_URL_FILE="current_url.txt"

# Function to get current URL
get_current_url() {
    if [ -f "tunnel.log" ]; then
        grep -o "https://[a-zA-Z0-9-]*\.trycloudflare\.com" tunnel.log | tail -1
    fi
}

# Function to log URL change
log_url_change() {
    local url="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] URL: $url" >> $URL_LOG_FILE
    echo "$url" > $CURRENT_URL_FILE
}

# Function to start URL tracking
start_tracking() {
    echo "🔍 Starting URL tracking..."
    echo "📋 This will monitor URL changes and log them"
    echo ""
    
    # Get initial URL
    local current_url=$(get_current_url)
    if [ -n "$current_url" ]; then
        echo "🌐 Current URL: $current_url"
        log_url_change "$current_url"
    else
        echo "❌ No URL found. Start tunnel first:"
        echo "   ./manage_external_access.sh start"
        return 1
    fi
    
    echo ""
    echo "🔄 Monitoring for URL changes..."
    echo "Press Ctrl+C to stop tracking"
    
    # Monitor loop
    while true; do
        local new_url=$(get_current_url)
        local last_url=$(cat $CURRENT_URL_FILE 2>/dev/null)
        
        if [ "$new_url" != "$last_url" ] && [ -n "$new_url" ]; then
            echo "🔄 URL changed: $last_url → $new_url"
            log_url_change "$new_url"
            echo "📋 URL logged to: $URL_LOG_FILE"
        fi
        
        sleep 30  # Check every 30 seconds
    done
}

# Function to show current URL
show_current() {
    if [ -f "$CURRENT_URL_FILE" ]; then
        local url=$(cat $CURRENT_URL_FILE)
        echo "🌐 Current URL: $url"
        echo ""
        echo "🧪 Test Commands:"
        echo "curl $url/health"
        echo "curl -X POST $url/query -H \"Content-Type: application/json\" -d '{\"query\": \"Hello\"}'"
    else
        echo "❌ No current URL found"
    fi
}

# Function to show URL history
show_history() {
    if [ -f "$URL_LOG_FILE" ]; then
        echo "📋 URL History:"
        echo "=============="
        tail -10 "$URL_LOG_FILE"
    else
        echo "❌ No URL history found"
    fi
}

# Function to get latest URL
get_latest() {
    local url=$(get_current_url)
    if [ -n "$url" ]; then
        echo "🌐 Latest URL: $url"
        log_url_change "$url"
    else
        echo "❌ No URL found"
    fi
}

# Main command handling
case "${1:-help}" in
    "start")
        start_tracking
        ;;
    "current")
        show_current
        ;;
    "history")
        show_history
        ;;
    "latest")
        get_latest
        ;;
    *)
        echo "Usage: $0 {start|current|history|latest}"
        echo ""
        echo "Commands:"
        echo "  start   - Start URL tracking"
        echo "  current - Show current URL"
        echo "  history - Show URL history"
        echo "  latest  - Get latest URL"
        echo ""
        echo "🎯 Benefits:"
        echo "  • Tracks URL changes automatically"
        echo "  • Logs all URL changes with timestamps"
        echo "  • Provides easy access to current URL"
        echo "  • Maintains URL history"
        exit 1
        ;;
esac

