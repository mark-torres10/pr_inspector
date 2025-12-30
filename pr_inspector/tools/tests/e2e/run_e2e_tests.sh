#!/bin/bash

# End-to-end test runner for PR Inspector MCP Server tools
# This script:
# 1. Starts the MCP server in the background
# 2. Waits for it to be ready
# 3. Runs all e2e tests
# 4. Stops the server

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../../" && pwd)"
SERVER_PID=""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Cleanup function to ensure server is stopped
cleanup() {
    if [ ! -z "$SERVER_PID" ]; then
        echo -e "\n${YELLOW}Cleaning up: Stopping MCP server (PID: $SERVER_PID)...${NC}"
        kill $SERVER_PID 2>/dev/null || true
        wait $SERVER_PID 2>/dev/null || true
        echo -e "${GREEN}✅ Server stopped${NC}\n"
    fi
}

# Register cleanup function to run on script exit
trap cleanup EXIT INT TERM

# Function to check if server is ready
wait_for_server() {
    local max_attempts=30
    local attempt=0
    
    echo -e "${YELLOW}Waiting for MCP server to be ready...${NC}"
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://127.0.0.1:8000/mcp > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Server is ready!${NC}\n"
            return 0
        fi
        
        attempt=$((attempt + 1))
        sleep 1
    done
    
    echo -e "${RED}❌ Server failed to start within $max_attempts seconds${NC}"
    return 1
}

# Start the MCP server
echo -e "${YELLOW}🚀 Starting MCP server...${NC}"
cd "$PROJECT_ROOT"

# Start server in background and capture PID
uv run pr-inspector > /tmp/pr_inspector_server.log 2>&1 &
SERVER_PID=$!

echo -e "${GREEN}Server started (PID: $SERVER_PID)${NC}"
echo -e "   Logs: /tmp/pr_inspector_server.log\n"

# Wait for server to be ready
if ! wait_for_server; then
    echo -e "${RED}❌ Failed to start server${NC}"
    echo -e "${YELLOW}Server logs:${NC}"
    cat /tmp/pr_inspector_server.log
    exit 1
fi

# Find all e2e test files
echo -e "${YELLOW}📋 Finding e2e test files...${NC}"
TEST_FILES=$(find "$SCRIPT_DIR" -name "test_*.py" -type f | sort)

if [ -z "$TEST_FILES" ]; then
    echo -e "${RED}❌ No e2e test files found in $SCRIPT_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}Found $(echo "$TEST_FILES" | wc -l | tr -d ' ') test file(s):${NC}"
echo "$TEST_FILES" | sed 's/^/   - /'
echo ""

# Run each test
PASSED=0
FAILED=0
FAILED_TESTS=()

for test_file in $TEST_FILES; do
    test_name=$(basename "$test_file")
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}Running: $test_name${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
    
    if cd "$PROJECT_ROOT" && uv run python "$test_file"; then
        echo -e "\n${GREEN}✅ $test_name PASSED${NC}\n"
        PASSED=$((PASSED + 1))
    else
        echo -e "\n${RED}❌ $test_name FAILED${NC}\n"
        FAILED=$((FAILED + 1))
        FAILED_TESTS+=("$test_name")
    fi
done

# Print summary
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}📊 Test Summary${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Passed: $PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}❌ Failed: $FAILED${NC}"
    echo -e "${RED}Failed tests:${NC}"
    for test in "${FAILED_TESTS[@]}"; do
        echo -e "   - $test"
    done
    exit 1
else
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
fi

