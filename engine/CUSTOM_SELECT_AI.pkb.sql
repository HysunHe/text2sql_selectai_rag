create or replace package body CUSTOM_SELECT_AI is

    procedure  CREATE_PROVIDER (
        p_provider IN varchar2,
        p_endpoint IN varchar2,
        p_auth IN varchar2
    )
    is
    begin
        insert into CUSTOM_SELECT_AI_PROVIDERS (
            PROVIDER,
            ENDPOINT,
            AUTH
        ) values (
            p_provider,
            p_endpoint,
            p_auth
        );
        commit;
    exception
        when others then
            rollback;
            DBMS_OUTPUT.PUT_LINE('ERROR CREATE_PROVIDER: ' || SQLERRM);
    end CREATE_PROVIDER;


    procedure DROP_PROVIDER (
        p_provider IN varchar2
    ) is
    begin
        delete from CUSTOM_SELECT_AI_PROVIDERS where PROVIDER = p_provider;
        commit;
    exception
        when NO_DATA_FOUND then
            DBMS_OUTPUT.PUT_LINE('ERROR: PROVIDER NOT FOUND');
        when others then
            rollback;
            DBMS_OUTPUT.PUT_LINE('ERROR DROP_PROVIDERL: ' || SQLERRM);
    end DROP_PROVIDER;


    procedure CREATE_PROFILE (
        p_profile_name IN varchar2,
        p_description IN varchar2,
        p_attributes IN CLOB
    ) is
        l_json_attributes JSON_OBJECT_T;
        l_provider varchar2(256);
        l_model varchar2(256);
        l_tempreture number;
        l_max_tokens number;
        l_stop_tokens varchar2(1000);
        l_object_list JSON_ARRAY_T;
        l_object_list_clob clob;
        MissingParameterException EXCEPTION;
    begin
        l_json_attributes := JSON_OBJECT_T(p_attributes);

        l_provider := NVL(
                NVL( l_json_attributes.get_String('provider'),l_json_attributes.get_String('PROVIDER')
            ), NULL);
        l_model := NVL(
                NVL( l_json_attributes.get_String('model'),l_json_attributes.get_String('MODEL')
            ), NULL);
        l_object_list := NVL(
                NVL( l_json_attributes.get_Array('object_list'),l_json_attributes.get_Array('OBJECT_LIST')
            ), NULL);

        IF l_object_list IS NOT NULL THEN l_object_list_clob := l_object_list.to_clob; END IF;

        IF l_provider IS NULL OR l_model IS NULL OR l_object_list IS NULL THEN
            DBMS_OUTPUT.PUT_LINE('ERROR: PROFILE INFORMATION IS NOT COMPLETE!!');
            raise MissingParameterException;
        END IF;

        insert into CUSTOM_SELECT_AI_PROFILES (
            PROFILE_NAME, DESCRIPTION, ATTRIBUTES, PROVIDER, MODEL, OBJECT_LIST
        ) values (
            p_profile_name, p_description, p_attributes, l_provider, l_model, l_object_list_clob
        );

        commit;

        DBMS_OUTPUT.PUT_LINE('PROFILE CREATED SUCCESSFULLY');

    exception
        when others then
            rollback;
            DBMS_OUTPUT.PUT_LINE('ERROR CREATING PROFILE: ' || SQLERRM);
    end CREATE_PROFILE;


    procedure DROP_PROFILE (
        p_profile_name IN varchar2
    ) is
    begin
        delete from CUSTOM_SELECT_AI_PROFILES where PROFILE_NAME = p_profile_name;
        commit;
        DBMS_OUTPUT.PUT_LINE('PROFILE DROPPED SUCCESSFULLY');
    exception
        when NO_DATA_FOUND then
            DBMS_OUTPUT.PUT_LINE('ERROR: PROFILE NOT FOUND');
        when others then
            rollback;
            DBMS_OUTPUT.PUT_LINE('ERROR DROPPING PROFILE: ' || SQLERRM);
    end DROP_PROFILE;


  function CLEANSQL (
        p_sql       in varchar2
    ) return varchar2 is
        l_sql varchar(32767);
    begin
        l_sql := TRIM(p_sql);
        l_sql := REGEXP_REPLACE(l_sql,'(^[[:space:]]*|[[:space:]]*$)');

        IF INSTR(l_sql, '```')=1
            THEN
            l_sql := SUBSTR(l_sql, INSTR(l_sql, CHR(10)) + 1);
            l_sql := REPLACE(l_sql,'```','');
        END IF;

        l_sql := REGEXP_REPLACE(l_sql,'(^[[:space:]]*|[[:space:]]*$)');
        l_sql := TRIM(';' FROM l_sql);
        return l_sql;
    end CLEANSQL;


    function VALIDSQL (
        p_sql in varchar2
    ) return varchar2 is
        l_cursor NUMBER := dbms_sql.open_cursor;
        l_valid varchar2(32767) := 'OK';
    begin
        begin
            DBMS_SQL.PARSE (l_cursor, p_sql, DBMS_SQL.native);
        EXCEPTION
            WHEN OTHERS THEN 
                l_valid := SQLERRM;
        end;
        dbms_sql.close_cursor(l_cursor);
        return l_valid;
    end VALIDSQL;


    function DESC_TABLE(
        p_schema_name in varchar2,
        p_table_name in varchar2
    ) return varchar2 is
        TABLE_COMMENT varchar(500);
        TABLE_INFO varchar(32767);
        COLUMN_INFO varchar(32767);
    begin
        select COMMENTS into TABLE_COMMENT
        from ALL_TAB_COMMENTS
        where OWNER=p_schema_name and TABLE_NAME = p_table_name;
        
        TABLE_INFO := '# CREATE TABLE "' || p_schema_name ||  '".' || '"' || p_table_name || '"';
        
        if TABLE_COMMENT is not null then
            TABLE_INFO := TABLE_INFO || ' ''' || TABLE_COMMENT || '''';
        end if;
        TABLE_INFO := TABLE_INFO || ' (';

        select listagg(COL_INFO, ',') into COLUMN_INFO
        from (
            select '"' || COLUMN_NAME || '"' ||' '||DATA_TYPE || COMMENTS as COL_INFO
            from (
                select A.COLUMN_NAME,
                    case when A.DATA_TYPE = 'VARCHAR2' then A.DATA_TYPE || '(' || A.DATA_LENGTH || ')'  else A.DATA_TYPE end as DATA_TYPE,
                    case when B.COMMENTS is not null then ' '''||B.COMMENTS || '''' else '' end as COMMENTS
                from ALL_TAB_COLUMNS A
                left join ALL_COL_COMMENTS B on A.OWNER=B.OWNER and A.TABLE_NAME=B.TABLE_NAME and A.COLUMN_NAME=B.COLUMN_NAME
                where A.OWNER=p_schema_name and A.TABLE_NAME= p_table_name
                order by COLUMN_ID asc
            )
        );

        TABLE_INFO := TABLE_INFO || COLUMN_INFO || ')';
        -- DBMS_OUTPUT.put_line(TABLE_INFO);
        return TABLE_INFO;
    end DESC_TABLE;


    function SHOWPROMPT(
        p_text varchar2,
        p_profile_name varchar2
    ) RETURN VARCHAR2 IS    
        l_object_list clob;
        l_object_list_array JSON_ARRAY_T;
        l_object_elem JSON_ELEMENT_T;
        l_object JSON_OBJECT_T;
        l_owner VARCHAR2(1024);
        l_table_name VARCHAR2(1024);
        l_prompt varchar(32767);
        l_table_prompt varchar2(32767);
        l_table_info varchar2(32767);
    begin
        SELECT OBJECT_LIST INTO l_object_list
        from CUSTOM_SELECT_AI_PROFILES
        where UPPER(PROFILE_NAME)=UPPER(p_profile_name);

        l_object_list_array := JSON_ARRAY_T(l_object_list);

        l_prompt := '[
    {
        "role" : "system",
        "content" : "You are a data analyst who is proficient in Oracle SQL. \n\nGiven an input Question, create a syntactically correct Oracle SQL query to run. \n - Pay attention to using only the column names that you can see in the schema description.\n - Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.\n - Please double check that the SQL query you generate is valid for Oracle Database.\n - Consider table name, schema name and column name to be case sensitive and enclose in double quotes.  - Only use the tables listed below. \n - If the table definition includes the table owner, you should include both the owner name and user-qualified table name in the Oracle SQL. - DO NOT keep empty lines in the middle of the Oracle SQL.\n - DO NOT write anything else except the Oracle SQL.\n - Always use table alias and easy to read column aliases. \n\nFor string comparisons in WHERE clause, CAREFULLY check if any string in the question is in DOUBLE QUOTES, and follow the rules: \n - If a string is in DOUBLE QUOTES, use case SENSITIVE comparisons with NO UPPER() function.\n - If a string is not in DOUBLE QUOTES, use case INSENSITIVE comparisons by using UPPER() function around both operands of the string comparison.\nNote: These rules apply strictly to string comparisons in the WHERE clause and do not affect column names, table names, or other query components.\n\n"
    },
    {
        "role" : "system",
        "content" : "### Oracle SQL tables with their properties: "
    },';
        
        FOR indx IN 0 .. l_object_list_array.get_size - 1
        LOOP
        l_object_elem := l_object_list_array.get(indx);
        l_object := TREAT (l_object_elem AS JSON_OBJECT_T);
        l_owner := NVL(l_object.get_string('owner'),l_object.get_string('OWNER'));
        l_table_name := NVL(l_object.get_string('name'),l_object.get_string('NAME'));

        DBMS_OUTPUT.PUT_LINE('Processing object ' || l_owner || '.' || l_table_name);
        begin
            l_table_info := DESC_TABLE(l_owner,l_table_name);
        l_table_info := REPLACE(l_table_info, '"', '\"');
            l_table_prompt := '
    {
        "role" : "system",
        "content" : "' || l_table_info || '"
    },';
            l_prompt := l_prompt || l_table_prompt;
        exception
                when NO_DATA_FOUND then
                    continue;
        end;
        END LOOP;
        l_prompt := l_prompt || '
    {
        "role" : "user",
        "content" : "' || p_text || '"
    }
    ]';
        return l_prompt;
    end SHOWPROMPT;


    -- Return text response generated by LLM
    function MAKE_LLM_REQUEST (
        p_prompt            IN VARCHAR2,
        p_profile_name      IN VARCHAR2,
        p_wallet_path       IN VARCHAR2 default null,
        p_wallet_pwd        IN VARCHAR2 default null,
        p_proxy             IN VARCHAR2 default null,
        p_no_proxy_domains  IN VARCHAR2 default null,
        p_temperature       IN NUMBER default 0.5,
        p_max_tokens        IN NUMBER default 4096 
    ) return varchar2
    is
        l_request_body  varchar2(32767);

        L_HTTP_REQUEST  UTL_HTTP.REQ;
        L_HTTP_RESPONSE UTL_HTTP.RESP;

        L_PROVIDER      varchar2(256);
        L_URL           varchar2(1024);
        L_TOKEN         varchar2(1024);
        L_RESPONSE_BODY clob;
        L_ANSWER        varchar2(32767);

        V_MODEL         varchar2(256);
    begin
        select PROVIDER, MODEL into L_PROVIDER, V_MODEL
        from CUSTOM_SELECT_AI_PROFILES
        where UPPER(PROFILE_NAME) = UPPER(p_profile_name);

        select PROVIDER, ENDPOINT, AUTH into L_PROVIDER, L_URL ,L_TOKEN
        from CUSTOM_SELECT_AI_PROVIDERS
        where UPPER(PROVIDER) = UPPER(L_PROVIDER);

        l_request_body := '{
        "model": "<MODEL>",
        "temperature": <TEMPERATURE>,
        "max_tokens": <MAX_TOKENS>,
        "stop": null,
        "stream": false,
        "messages": <CONTENT>   
    }';

        -- Construct request body
        l_request_body := REPLACE(l_request_body,'<CONTENT>',p_prompt);
        l_request_body := REPLACE(l_request_body,'<MODEL>',V_MODEL);
        l_request_body := REPLACE(l_request_body,'<TEMPERATURE>',TO_CHAR(p_temperature, '999990D99'));
        l_request_body := REPLACE(l_request_body,'<MAX_TOKENS>',TO_CHAR(p_max_tokens));

        DBMS_OUTPUT.put_line(l_request_body);

        -- Open HTTP request
        IF p_wallet_path IS NOT NULL THEN
            UTL_HTTP.set_wallet('file:'||p_wallet_path, p_wallet_pwd);
        END IF;

        IF p_proxy IS NOT NULL THEN
            UTL_HTTP.set_proxy(proxy => p_proxy, no_proxy_domains => p_no_proxy_domains);
        END IF;

        L_HTTP_REQUEST := UTL_HTTP.BEGIN_REQUEST(URL => L_URL, METHOD => 'POST', HTTP_VERSION => 'HTTP/1.1');

        UTL_HTTP.set_header(l_http_request, 'Content-Type', 'application/json');
        UTL_HTTP.set_header(l_http_request, 'Accept', 'application/json');
        UTL_HTTP.set_header(l_http_request, 'Authorization', 'Bearer ' || l_token);

        UTL_HTTP.SET_BODY_CHARSET(L_HTTP_REQUEST, 'UTF-8');
        UTL_HTTP.SET_HEADER(L_HTTP_REQUEST, 'Content-Length', LENGTHB(l_request_body));

        UTL_HTTP.WRITE_TEXT(L_HTTP_REQUEST, l_request_body);

        L_HTTP_RESPONSE := UTL_HTTP.GET_RESPONSE(L_HTTP_REQUEST);
        UTL_HTTP.READ_TEXT(L_HTTP_RESPONSE, L_RESPONSE_BODY);
        UTL_HTTP.END_RESPONSE(L_HTTP_RESPONSE);
        -- L_RESPONSE_BODY := REPLACE(L_RESPONSE_BODY, '''', '''''');

        DBMS_OUTPUT.put_line('Response: ' || l_response_body);

        execute immediate 'SELECT JSON_VALUE(:1,''$.choices[0].message.content'') FROM DUAL' into L_ANSWER USING l_response_body;

        L_ANSWER := trim(L_ANSWER);

        if SUBSTR(L_ANSWER, -1) = ';' then
            L_ANSWER := SUBSTR(L_ANSWER, 1, LENGTH(L_ANSWER) - 1);
        end if;

        if L_ANSWER is not null then
            return L_ANSWER;
        else
            return L_RESPONSE_BODY;
        end if;
    exception
        when UTL_HTTP.TOO_MANY_REQUESTS then
            return 'HTTP 429 Too Many Requests';
        when OTHERS then
            return 'HTTP Request Failed: ' || SUBSTR(DBMS_UTILITY.format_error_stack, 1, 500);
    end MAKE_LLM_REQUEST;


    function CHAT (
        p_user_text         IN VARCHAR2,
        p_profile_name      IN VARCHAR2,
        p_system_text       IN VARCHAR2 default null,
        p_user              IN VARCHAR2 default null,
        p_wallet_path       IN VARCHAR2 default null,
        p_wallet_pwd        IN VARCHAR2 default null,
        p_proxy             IN VARCHAR2 default null,
        p_no_proxy_domains  IN VARCHAR2 default null
    ) return varchar2 is
        l_prompt            VARCHAR2(4000);
    begin
        if p_system_text is not null then
            l_prompt := '[
            {"role": "system","content": "' || p_system_text || '"},
            {"role": "user","content": "' || p_user_text || '"}
            ]';
        else
            l_prompt := '[
            {"role": "user","content": "' || p_user_text || '"}
            ]';
        end if;

        return MAKE_LLM_REQUEST(
            p_prompt => l_prompt,
            p_profile_name => p_profile_name,
            p_wallet_path => p_wallet_path,
            p_wallet_pwd => p_wallet_pwd,
            p_proxy => p_proxy,
            p_no_proxy_domains => p_no_proxy_domains,
            p_temperature => 0.6,
            p_max_tokens => 4096
        );
    end CHAT;
    

    function SHOWSQL (
        p_text              IN VARCHAR2,
        p_profile_name      IN VARCHAR2,
        p_user              IN VARCHAR2 default null,
        p_request_id        IN VARCHAR2 default null,
        p_wallet_path       IN VARCHAR2 default null,
        p_wallet_pwd        IN VARCHAR2 default null,
        p_proxy             IN VARCHAR2 default null,
        p_no_proxy_domains  IN VARCHAR2 default null
    ) return varchar2 
    is
        l_prompt            VARCHAR2(32767);
        l_sql               VARCHAR2(32767);
        l_valid             VARCHAR2(32767);
        PRAGMA AUTONOMOUS_TRANSACTION;
    begin
        l_prompt := SHOWPROMPT(
            p_profile_name => p_profile_name,
            p_text => p_text
        );

        l_sql := MAKE_LLM_REQUEST(
            p_prompt => l_prompt,
            p_profile_name => p_profile_name,
            p_wallet_path => p_wallet_path,
            p_wallet_pwd => p_wallet_pwd,
            p_proxy => p_proxy,
            p_no_proxy_domains => p_no_proxy_domains,
            p_temperature => 0.01,
            p_max_tokens => 4096
        );

        DBMS_OUTPUT.put_line(l_sql);

        l_sql := CLEANSQL(l_sql);
        l_valid := VALIDSQL(l_sql);

        if l_valid <> 'OK' then
            DBMS_OUTPUT.put_line('LlmCapabilityLimitException: ' || l_valid);
            return 'LlmCapabilityLimitException: Failure to generate SQL! ' || l_valid;
        end if;

        if p_request_id is not null then
            insert into CUSTOM_SELECT_AI_EMBEDDINGS(
                user_name,
                request_id,
                question,
                sql_text,
                embedding
            ) values (
                p_user,
                p_request_id,
                p_text,
                l_sql,
                dbms_vector.utl_to_embedding(
                    p_text,
                    json('{
                        "provider": "OCIGenAI",
                        "credential_name": "VECTOR_OCI_GENAI_CRED",
                        "url": "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com/20231130/actions/embedText",
                        "model": "cohere.embed-multilingual-v3.0"
                    }')
                )
            );
            commit;
        end if;

        return l_sql;
    end SHOWSQL;


    PROCEDURE RUNSQL (
        p_text              IN VARCHAR2,
        p_profile_name      IN VARCHAR2,
        p_max_rows          IN NUMBER default 20,
        p_user              IN VARCHAR2 default null,
        p_request_id        IN VARCHAR2 default null,
        p_wallet_path       IN VARCHAR2 default null,
        p_wallet_pwd        IN VARCHAR2 default null,
        p_proxy             IN VARCHAR2 default null,
        p_no_proxy_domains  IN VARCHAR2 default null
    ) is
        l_sql               VARCHAR2(4000);
        v_result            SYS_REFCURSOR;
    begin
        l_sql := SHOWSQL(
            p_text => p_text,
            p_profile_name => p_profile_name,
            p_user => p_user,
            p_request_id => p_request_id,
            p_wallet_path => p_wallet_path,
            p_wallet_pwd => p_wallet_pwd,
            p_proxy => p_proxy,
            p_no_proxy_domains => p_no_proxy_domains
        );

        IF INSTR(lower(l_sql),'fetch ') = 0 THEN 
            l_sql := l_sql ||' FETCH FIRST ' || p_max_rows || ' ROWS ONLY';
        END IF;

        OPEN v_result FOR l_sql;
        DBMS_SQL.RETURN_RESULT(cur);
    end RUNSQL;

end CUSTOM_SELECT_AI;
/