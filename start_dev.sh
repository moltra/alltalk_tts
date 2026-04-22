#!/usr/bin/env bash
source ~/.bashrc
source ${ALLTALK_DIR}/conda_env.sh

echo "Starting AllTalk in development mode..."
echo "Code is mounted from host - changes reflect immediately"
echo "Gradio will be available on port 7852"
echo "API will be available on port 7851"
echo ""
echo "To run with debugger: python -m ipdb tts_server.py"
echo "To run tests: pytest"
echo ""

# Download models at runtime if not present
if [ ! -d "models/${TTS_MODEL}" ]; then
  echo "Downloading TTS models..."
  python ./system/config/firstrun.py --tts_model ${TTS_MODEL}
fi

# Start API server in background
echo "Starting API server on port 7851..."
python tts_server.py &
API_PID=$!

# Wait for API server to be ready
sleep 5

# Start Gradio UI
echo "Starting Gradio UI on port 7852..."
python script.py

# If Gradio exits, kill API server
kill $API_PID 2>/dev/null
