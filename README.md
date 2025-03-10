## 免责声明
这是一个基于 Oracle 23ai 数据库 与 第三方或自部署大语言模型做的一个Demo，不是一个开箱即用的成品，此Demo属于个人作品，非官方提供的产品组件。作者及Oracle公司不负责Demo代码的质量保障。如果使用此Demo或其中一部分造成任何损失，后果自负。

下载此Demo应用代表您接受以上免责声明。


## 介绍

AiReport Project。此项目主要使用自己部署的大语言模型、Oracle数据库（包括向量、JSON、关系）实现文生SQL(text2sql)，以及采用 RAG 的方式来解决 SQL 生成的正确率问题，通过RAG来达到持续训练持续提升准确率的效果。Text2SQL 及 RAG 引擎部分采用 PLSQL 实现，中间逻辑控制部分采用 Python 实现，前端页面采用 Oracle APEX 低代码实现。

RAG知识库采用持续收集、持续学习的思想，让 Text2SQL 越用越准确。


## 架构
![alt text](image_arch.png)


## Python版本

运行该程序需要 Python 3.12。例如，可以使用 conda 或 poetry 创建一个 python 虚拟环境：

```shell
conda create -n aireport python=3.12
```

## 数据库配置
### 创建数据库对象
安装顺序如下（./engine 目录下）：
1. 执行 CUSTOM_SELECT_AI_TABLES.sql
2. 执行 CUSTOM_SELECT_AI.pkg.sql
3. 执行 CUSTOM_SELECT_AI.pkb.sql

执行完以上三步，就代表安装完成，完成如下的配置后，就可以直接使用了。


## LLM 配置
### 配置大语言模型提供商
下例配置了使用通义千问的云服务。也可以使用其它厂商的或自己部署的LLM。要求是配置OpenAI兼容的接口。

以下以自己部署的大模型为例。

#### 部署大语言模型LLM
关于安装 vLLM，不再赘述。

部署 Qwen2.5-Coder-14B-Instruct-AWQ 模型到 A10（单台就可以部署起来）
```shell
nohup python -u -m vllm.entrypoints.openai.api_server --port 8098 --model Qwen/Qwen2.5-Coder-14B-Instruct-AWQ --served-model-name Qwen2.5-Coder-14B-Instruct-AWQ --device=cuda --dtype auto --max-model-len=8192 > vllm.out 2>&1 &
```

允许数据库访问 LLM 服务器（简单起见，这里直接给了 *，代表所有地址都允许访问）
```sql
BEGIN
   -- allow connecting to outside hosts
    DBMS_NETWORK_ACL_ADMIN.APPEND_HOST_ACE(
        host => '*',
        ace => xs$ace_type(privilege_list => xs$name_list('connect'),
                           principal_name => 'HYSPOC',
                           principal_type => xs_acl.ptype_db));
END;
/
```

部署完成后，测试一下的接口的连通性：
```shell
curl http://132.145.95.18:8098/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "Qwen2.5-Coder-14B-Instruct-AWQ",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Tell me something about large language models."}
        ]
    }'
```

### 创建 Provider，指向自己部署的模型
```sql
BEGIN
  CUSTOM_SELECT_AI.CREATE_PROVIDER(
		p_provider    =>    'qwen',
		p_endpoint    =>    'http://132.145.95.18:8098/v1/chat/completions',
		p_auth        =>    'EMPTY'
	);
END;
/
```

### 创建 Profile，指定需要利用哪些数据库对象 以及 用来生成SQL 的 LLM 模型名称
Profile指定了使用哪个模型，以及Text2SQL时需要用到的数据库对象（表或视图）。
```sql
BEGIN
	CUSTOM_SELECT_AI.CREATE_PROFILE(
      p_profile_name    =>'HKE_DEMO',
      p_description     => 'SelectAI DEMO for HKE',
      p_attributes      => '{
          "provider": "qwen",
          "model" : "Qwen2.5-Coder-14B-Instruct-AWQ",
          "object_list": [{"owner": "POCUSER", "name": "HKE_PROD_DEFECT"},
                          {"owner": "POCUSER", "name": "HKE_PROD_OUT_YIELD_QTY"}
                          ]
      }'
    );
END;
/
```

### 创建 Embedding Config

RAG的向量化过程需要用到。可以是兼容OpenAI消息格式的任何模型，包括自己部署的本地Embedding模型 或 云服务都可以。如果SHOWSQL不指定，则使用这里配置的 ID 为 DEFAULT 的 Embedding 配置。

```sql
BEGIN
  CUSTOM_SELECT_AI.CREATE_EMBEDDING_CONF(
        p_conf_id     =>    'DEFAULT',
		p_provider    =>    'OCIGenAI',
        p_model       =>    'cohere.embed-multilingual-v3.0',
		p_endpoint    =>    'https://inference.generativeai.us-chicago-1.oci.oraclecloud.com/20231130/actions/embedText',
		p_credential  =>    'VECTOR_OCI_GENAI_CRED'
	);
END;
/

```

注意：上面的 p_credential，需要使用 dbms_vector.create_credential 创建。具体请参阅 Oracle 的官方文档【https://docs.oracle.com/en/database/oracle/oracle-database/23/arpls/dbms_vector1.html】。

以上是用 Oracle OCI 的 Embedding 模型，也可以是其它的模型，比如用 千问(QWen) Embedding 或者是 自己部署的 Embedding 模型。如下是使用 千问(QWen) Embedding 的例子：

```sql
BEGIN
  CUSTOM_SELECT_AI.CREATE_EMBEDDING_CONF(
        p_conf_id     =>    'qwen_embedding',
		p_provider    =>    'OpenAI',
        p_model       =>    'text-embedding-v3',
		p_endpoint    =>    'https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings',
		p_credential  =>    'HYSUN_ALIYUN_CRED'
	);
END;
/
```


## 接口及样例
### CHAT接口 - 直接与 LLM 聊天
```sql
select CUSTOM_SELECT_AI.CHAT(
    p_profile_name  => 'HKE_DEMO',
    p_user_text     => '你好',
    p_system_text   => '你是一个积极的、充满正能量的人工智能助手。'
);
```

### EMBEDDING接口 - 文本转向量
```sql
select CUSTOM_SELECT_AI.EMBEDDING(
    p_text => '将文本转成向量',
    p_embedding_conf => 'DEFAULT'
);
```

### SHOWSQL接口 - 自然语言生成SQL
此方法将自然语言生成对应的SQL语句
```sql
select CUSTOM_SELECT_AI.SHOWSQL(
  	p_profile_name => 'HKE_DEMO',
    p_embedding_conf => 'DEFAULT',
  	p_user_text => '查询符合条件的各YIELD小等级占比（即YIELD_QTY之和/OUT_QTY之和），条件为：公司名称为COMPANY1，工厂名称为FACTORYNAME1，产品名称为PRODUCT1。占比用百分比表示并排序，用中文别名返回。'
);
```

## 配置Demo应用

Demo应用是AI Report的一个参考实现，其使用了上述 SHOWSQL 接口及 CHAT 接口等，前端 UI 采用 Oracle 低代码平台 APEX 实现，后端服务采用 Python 实现。Demo应用本身不复杂，因此不作详细描述，读者可自己参阅源代码。

### Python包依赖

pip install -r requirements.txt

### 环境变量配置

服务启动时，会从文件 app.env 中读取环境变量信息。

### Demo应用DDL建表
TODO

### 启动Demo应用服务

start.sh: 启动或重启。如果程序已经在运行，那么运行start.sh时将先杀掉正在运行的进程，再启动新的进程。


## Demo应用UI界面
### RAG 知识库管理界面 (Oracle APEX 实现)
系统自动记录用户每次数据查询时生成的SQL语句，通过将正确的SQL语句持续不断的加入到知识库中，达到持续训练的目的，因此，系统会越用越准确。


![alt text](image_rag_store.png)

### 用户聊天界面 (Oracle APEX 实现)

![alt text](image_chat.png)


## 附录 (Appendix)

### 配置使用云厂端API服务，供参考

```sql
----- Create service provider
BEGIN
  CUSTOM_SELECT_AI.CREATE_PROVIDER(
		p_provider    =>    'qwen',
		p_endpoint    =>    'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
		p_auth        =>    'sk-75229e7exxxxxxxxxxxxxxxxxxxxxxxx'
	);
END;
/

----- Create profile
BEGIN
	CUSTOM_SELECT_AI.CREATE_PROFILE(
      p_profile_name    =>'HKE_DEMO',
      p_description     => 'SelectAI DEMO for HKE',
      p_attributes      => '{
          "provider": "qwen",
          "model" : "qwen-max-2025-01-25",
          "object_list": [{"owner": "POCUSER", "name": "HKE_PROD_DEFECT"},
                          {"owner": "POCUSER", "name": "HKE_PROD_OUT_YIELD_QTY"}
                          ]
      }'
    );
END;
/
```


### 演示场景 (Demo Script)

利用样例数据，列出两个演示/测试场景：

### 场景一，查询不良排名数据：
对话流程：
1. 输入 “显示不良排名”
2. 继续输入 “只显示company1公司的”
3. 继续输入 “只显示product1的”
3. 继续输入 “只显示product2的”


### 场景二，查询YIELD小等级占比数据：
对话流程：
1. 输入 “查询company1公司生产的product1产品各YIELD小等级占比”
2. 请提供您需要查询的工厂名称？===> 输入“factoryname1”
3. 继续输入 “company2公司生产的product2呢”
4. 完成对话。
