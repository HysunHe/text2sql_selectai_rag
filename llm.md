### 部署 LLM
nohup python -u -m vllm.entrypoints.openai.api_server --port 8098 --model Qwen/Qwen2.5-14B-Instruct-AWQ --served-model-name Qwen2.5-14B-Instruct-AWQ --device=cuda --dtype auto --max-model-len=4096 > vllm.out 2>&1 &

### 测试部署结果
curl http://132.145.95.18:8098/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "Qwen2.5-14B-Instruct-AWQ",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Tell me something about large language models."}
        ]
    }'