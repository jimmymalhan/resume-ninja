#!/bin/bash

# Check if port 8000 is in use
if lsof -Pi :8000 -sTCP:LISTEN >/dev/null; then
  # Get the PID of the process using port 8000
  pid=$(lsof -Pi :8000 -sTCP:LISTEN -t)

  echo "Process running on port 8000 with PID: $pid"

  # Terminate the process
  kill $pid

  echo "Process terminated."
else
  echo "No process running on port 8000."
fi
