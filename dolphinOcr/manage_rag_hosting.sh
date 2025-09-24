#!/bin/bash

# RAG API Hosting Management Script
# Manages the Universal RAG API service on Unity server

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

case "${1:-help}" in
    "start")
        echo "🚀 Starting RAG API Hosting Service..."
        JOB_ID=$(sbatch run_universal_rag_hosting.slurm | awk '{print $4}')
        echo "✅ RAG API hosting job submitted with ID: $JOB_ID"
        echo "📋 Monitor with: ./manage_rag_hosting.sh status"
        echo "🔗 Check logs with: ./manage_rag_hosting.sh logs"
        ;;
    "stop")
        echo "🛑 Stopping RAG API Hosting Service..."
        # Find running RAG API jobs
        RUNNING_JOBS=$(squeue -u $USER --name=rag_api_host --format="%i" --noheader)
        if [ -n "$RUNNING_JOBS" ]; then
            for job_id in $RUNNING_JOBS; do
                echo "Stopping job $job_id..."
                scancel $job_id
            done
            echo "✅ RAG API hosting jobs stopped"
        else
            echo "ℹ️  No RAG API hosting jobs running"
        fi
        ;;
    "status")
        echo "📊 RAG API Hosting Status"
        echo "========================="
        echo ""
        echo "🔍 Running Jobs:"
        squeue -u $USER --name=rag_api_host
        echo ""
        echo "🔍 Recent Job History:"
        sacct -u $USER --name=rag_api_host --format=JobID,JobName,State,Start,End,ExitCode --starttime=today
        echo ""
        echo "🔍 Node Information:"
        if [ -f "logs/rag_api.pid" ]; then
            PID=$(cat logs/rag_api.pid)
            NODE=$(squeue -u $USER --name=rag_api_host --format="%N" --noheader | head -1)
            if [ -n "$NODE" ]; then
                echo "Node: $NODE"
                echo "PID: $PID"
                echo "API URL: http://$NODE:8080"
                echo "Health Check: http://$NODE:8080/health"
            fi
        else
            echo "No active RAG API process found"
        fi
        ;;
    "logs")
        echo "📋 RAG API Logs"
        echo "==============="
        if [ -f "logs/rag_api.log" ]; then
            echo "📄 Server Logs (last 50 lines):"
            tail -50 logs/rag_api.log
        else
            echo "No server logs found"
        fi
        echo ""
        echo "📄 SLURM Output:"
        ls -la slurm_output/rag_api_host_*.out 2>/dev/null | tail -1 | while read line; do
            echo "File: $line"
            tail -20 "$line"
        done
        ;;
    "test")
        echo "🧪 Testing RAG API Connection..."
        if [ -f "logs/rag_api.pid" ]; then
            NODE=$(squeue -u $USER --name=rag_api_host --format="%N" --noheader | head -1)
            if [ -n "$NODE" ]; then
                echo "Testing connection to http://$NODE:8080..."
                if curl -s http://$NODE:8080/health > /dev/null; then
                    echo "✅ RAG API is responding!"
                    echo "📊 Health Status:"
                    curl -s http://$NODE:8080/health | python -m json.tool
                else
                    echo "❌ RAG API is not responding"
                fi
            else
                echo "❌ No active RAG API node found"
            fi
        else
            echo "❌ No RAG API process found"
        fi
        ;;
    "query")
        if [ -z "$2" ]; then
            echo "Usage: $0 query \"your question here\""
            exit 1
        fi
        echo "🔍 Querying RAG API..."
        if [ -f "logs/rag_api.pid" ]; then
            NODE=$(squeue -u $USER --name=rag_api_host --format="%N" --noheader | head -1)
            if [ -n "$NODE" ]; then
                echo "Query: $2"
                echo "API: http://$NODE:8080"
                echo ""
                curl -s -X POST http://$NODE:8080/query \
                    -H "Content-Type: application/json" \
                    -d "{\"query\": \"$2\"}" | python -m json.tool
            else
                echo "❌ No active RAG API node found"
            fi
        else
            echo "❌ No RAG API process found"
        fi
        ;;
    "url")
        echo "🔗 RAG API URLs"
        echo "==============="
        if [ -f "logs/rag_api.pid" ]; then
            NODE=$(squeue -u $USER --name=rag_api_host --format="%N" --noheader | head -1)
            if [ -n "$NODE" ]; then
                echo "🌐 API Base URL: http://$NODE:8080"
                echo "❤️  Health Check: http://$NODE:8080/health"
                echo "📚 API Docs: http://$NODE:8080/docs"
                echo "🔍 Query Endpoint: http://$NODE:8080/query"
                echo "⚙️  Models Endpoint: http://$NODE:8080/models"
                echo ""
                echo "📋 For your Next.js app:"
                echo "NEXT_PUBLIC_RAG_API_URL=http://$NODE:8080"
            else
                echo "❌ No active RAG API node found"
            fi
        else
            echo "❌ No RAG API process found"
        fi
        ;;
    "restart")
        echo "🔄 Restarting RAG API Hosting Service..."
        $0 stop
        sleep 5
        $0 start
        ;;
    "help"|*)
        echo "RAG API Hosting Management"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  start     - Start RAG API hosting service"
        echo "  stop      - Stop RAG API hosting service"
        echo "  restart   - Restart RAG API hosting service"
        echo "  status    - Show hosting status and job information"
        echo "  logs      - Show server and SLURM logs"
        echo "  test      - Test API connection and health"
        echo "  query     - Send a test query to the API"
        echo "  url       - Show API URLs for integration"
        echo "  help      - Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 start                    # Start the hosting service"
        echo "  $0 status                   # Check if it's running"
        echo "  $0 test                     # Test the API"
        echo "  $0 query \"What is AI?\"      # Send a test query"
        echo "  $0 url                      # Get URLs for your Next.js app"
        echo ""
        echo "Integration:"
        echo "  Use the URLs from 'url' command in your Next.js app"
        echo "  Set NEXT_PUBLIC_RAG_API_URL to the base URL"
        echo "  Use the client libraries in client-libraries/ directory"
        ;;
esac
