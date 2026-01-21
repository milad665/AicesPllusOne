#!/bin/bash

# Start the API Server
echo "Starting API Server..."
python -m src.api &
API_PID=$!

# Start the React UI
echo "Starting React UI..."
cd ui
npm run dev &
UI_PID=$!

# Handle shutdown
trap "kill $API_PID $UI_PID" EXIT

wait
