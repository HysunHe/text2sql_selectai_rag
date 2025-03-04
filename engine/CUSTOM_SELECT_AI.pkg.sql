create or replace package CUSTOM_SELECT_AI is

    procedure CREATE_PROVIDER (
        p_provider varchar2,
        p_endpoint varchar2,
        p_auth varchar2 DEFAULT NULL
    );

    procedure DROP_PROVIDER (
        p_provider varchar2
    );

    procedure CREATE_PROFILE (
        p_profile_name varchar2,
        p_description varchar2,
        p_attributes CLOB
    );

    procedure DROP_PROFILE (
        p_profile_name varchar2
    );

    function DESC_TABLE(
        p_schema_name in varchar2,
        p_table_name in varchar2
    ) return varchar2;

    function VALIDSQL (
        p_sql in varchar2
    ) return varchar2;

    function SHOWPROMPT(
        p_user_text         IN VARCHAR2,
        p_profile_name      IN VARCHAR2,
        p_ref_count         IN NUMBER default 5
    ) return varchar2;

    function MAKE_LLM_REQUEST (
        p_prompt            IN VARCHAR2,
        p_profile_name      IN VARCHAR2,
        p_wallet_path       IN VARCHAR2 default null,
        p_wallet_pwd        IN VARCHAR2 default null,
        p_proxy             IN VARCHAR2 default null,
        p_no_proxy_domains  IN VARCHAR2 default null,
        p_temperature       IN NUMBER default 0.5,
        p_max_tokens        IN NUMBER default 4096 
    ) return varchar2;

    function CHAT (
        p_user_text         IN VARCHAR2,
        p_profile_name      IN VARCHAR2,
        p_system_text       IN VARCHAR2 default null,
        p_user              IN VARCHAR2 default null,
        p_wallet_path       IN VARCHAR2 default null,
        p_wallet_pwd        IN VARCHAR2 default null,
        p_proxy             IN VARCHAR2 default null,
        p_no_proxy_domains  IN VARCHAR2 default null
    ) return varchar2;

    function SHOWSQL(
        p_user_text         IN VARCHAR2,
        p_profile_name      IN VARCHAR2,
        p_max_rows          IN NUMBER default 20,
        p_ref_count         IN NUMBER default 5,
        p_user              IN VARCHAR2 default null,
        p_request_id        IN VARCHAR2 default null,
        p_wallet_path       IN VARCHAR2 default null,
        p_wallet_pwd        IN VARCHAR2 default null,
        p_proxy             IN VARCHAR2 default null,
        p_no_proxy_domains  IN VARCHAR2 default null
    ) return varchar2;

end CUSTOM_SELECT_AI;
/