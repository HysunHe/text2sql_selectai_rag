set serveroutput on;

EXEC CUSTOM_SELECT_AI.DROP_PROVIDER('qwen');

BEGIN
  CUSTOM_SELECT_AI.CREATE_PROVIDER(
		p_provider    =>    'qwen',
		p_endpoint    =>    'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
		p_auth        =>    'sk-75229e7e569449129daf5eed56440003'
	);
END;
/

BEGIN
	CUSTOM_SELECT_AI.CREATE_PROFILE(
      p_profile_name    =>'HKE_DEMO',
      p_description     => 'SelectAI DEMO for HKE',
      p_attributes      => '{
          "provider": "qwen",
          "model" : "qwen-max-2025-01-25",
          "object_list": [{"owner": "POCUSER", "name": "HKE_PROD_DEFECT"},
                          {"owner": "POCUSER", "name": "HKE_PROD_OUT_YEILD_QTY"}
                          ]
      }'
    );
END;
/

select CUSTOM_SELECT_AI.CHAT(
  p_profile_name => 'HKE_DEMO',
  p_text => 'hello'
);

select CUSTOM_SELECT_AI.SHOWSQL(
  p_profile_name => 'HKE_DEMO',
  p_text => '查询符合条件的各YIELD小等级占比（即YIELD_QTY之和/OUT_QTY之和），条件为：公司名称为COMPANY1，工厂名称为FACTORYNAME1，产品名称为PRODUCT1。占比用百分比表示并排序，用中文别名返回。'
);


SELECT dbms_vector.utl_to_embedding(
    'This is a test',
    json('{
        "provider": "OCIGenAI",
        "credential_name": "VECTOR_OCI_GENAI_CRED",
        "url": "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com/20231130/actions/embedText",
        "model": "cohere.embed-multilingual-v3.0"
    }')
);

select * FROM user_credentials;

BEGIN
    DBMS_NETWORK_ACL_ADMIN.APPEND_HOST_ACE(
        host => '*',
        ace => xs$ace_type(privilege_list => xs$name_list('connect'),
                           principal_name => 'POCUSER',
                           principal_type => xs_acl.ptype_db));
END;
/


set serveroutput on;
declare
 l_user_prompt       VARCHAR2(4000);
  p_user_text varchar2(1000) := '## <用户问题>:
                你好';
begin
        l_user_prompt := REPLACE(REPLACE(p_user_text,CHR(13),'\n'),CHR(10),'\n');
        l_user_prompt := REPLACE(l_user_prompt,'"','\"');
    dbms_output.put_line(l_user_prompt);
end;
/