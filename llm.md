### 允许数据库访问服务器
BEGIN
   -- allow connecting to outside hosts
    DBMS_NETWORK_ACL_ADMIN.APPEND_HOST_ACE(
        host => '*',
        ace => xs$ace_type(privilege_list => xs$name_list('connect'),
                           principal_name => 'HYSPOC',
                           principal_type => xs_acl.ptype_db));
END;
/

### 部署 LLM
nohup python -u -m vllm.entrypoints.openai.api_server --port 8098 --model Qwen/Qwen2.5-14B-Instruct-AWQ --served-model-name Qwen2.5-14B-Instruct-AWQ --device=cuda --dtype auto --max-model-len=8192 > vllm.out 2>&1 &

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

### 部署 Coder LLM
nohup python -u -m vllm.entrypoints.openai.api_server --port 8098 --model Qwen/Qwen2.5-Coder-14B-Instruct-AWQ --served-model-name Qwen2.5-Coder-14B-Instruct-AWQ --device=cuda --dtype auto --max-model-len=8192 > vllm.out 2>&1 &

### 测试 Coder 模型部署结果
curl http://132.145.95.18:8098/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "Qwen2.5-Coder-14B-Instruct-AWQ",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Tell me something about large language models."}
        ]
    }'
