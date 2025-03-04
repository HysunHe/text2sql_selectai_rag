set serveroutput on;

EXEC CUSTOM_SELECT_AI.DROP_PROVIDER('qwen');
EXEC CUSTOM_SELECT_AI.DROP_PROFILE('HKE_DEMO');


------------------ Cloud --------------------
----- Create service provider
BEGIN
  CUSTOM_SELECT_AI.CREATE_PROVIDER(
		p_provider    =>    'qwen',
		p_endpoint    =>    'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
		p_auth        =>    'sk-75229e7e569449129daf5eed56440003'
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


------------------ Local Deployed Qwen2.5-14B-Instruct On A10 --------------------
------ Create local provider
BEGIN
  CUSTOM_SELECT_AI.CREATE_PROVIDER(
		p_provider    =>    'qwen',
		p_endpoint    =>    'http://132.145.95.18:8098/v1/chat/completions',
		p_auth        =>    'EMPTY'
	);
END;
/

------ Create profile
BEGIN
	CUSTOM_SELECT_AI.CREATE_PROFILE(
      p_profile_name    =>'HKE_DEMO',
      p_description     => 'SelectAI DEMO for HKE',
      p_attributes      => '{
          "provider": "qwen",
          "model" : "Qwen2.5-14B-Instruct-AWQ",
          "object_list": [{"owner": "POCUSER", "name": "HKE_PROD_DEFECT"},
                          {"owner": "POCUSER", "name": "HKE_PROD_OUT_YIELD_QTY"}
                          ]
      }'
    );
END;
/


------------------ Local Deployed Qwen2.5-Coder-14B-Instruct On A10 --------------------
------ Create provider (local deployed)
BEGIN
  CUSTOM_SELECT_AI.CREATE_PROVIDER(
		p_provider    =>    'qwen',
		p_endpoint    =>    'http://132.145.95.18:8098/v1/chat/completions',
		p_auth        =>    'EMPTY'
	);
END;
/

------ Create profile
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

select CUSTOM_SELECT_AI.CHAT(
  p_profile_name => 'HKE_DEMO',
  p_user_text => 'hello'
);

select CUSTOM_SELECT_AI.SHOWSQL(
  p_profile_name => 'HKE_DEMO',
  p_user_text => '查询符合条件的各YIELD小等级占比（即YIELD_QTY之和/OUT_QTY之和），条件为：公司名称为COMPANY1，工厂名称为FACTORYNAME1，产品名称为PRODUCT1。占比用百分比表示并排序，用中文别名返回。'
);

