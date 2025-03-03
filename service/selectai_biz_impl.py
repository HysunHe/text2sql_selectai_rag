""" 
Description: 
 - Implementation of the business logic for this project.

History:
 - 2025/01/20 by Hysun (hysun.he@oracle.com): Initial version
"""

import uuid
import json
import logging
from dao import selectai_util
from dao import dao_sql
from conf import app_config
from appcache import result_cache, user_context
from myutils import util_funcs
from typing import Optional, Dict, List, Any

_logger = logging.getLogger(__name__)


def determine_intent(user: str, ask: str) -> str:
    intent = dao_sql.get_accurate_intent_by_utterance(ask)
    if intent is None:
        supervised_intent_list = dao_sql.list_all_intents()
        intent = selectai_util.chat(
            user,
            f"""
                ## INSTRUCTION
                你是一个准确的问题分类助手。请根据提供的<问题类别列表>和<历史对话>，按以下规则将<用户问题>分类：
                1. <用户问题>必须准确归类为<问题类别列表>中的一个。
                2. 如果无法准确判断，请直接输出"其它类别"；
                3. 如果用户问题在<历史对话>中已经问过，请直接输出历史对话中的答案。
                
                ## <问题类别列表>
                ```
                {supervised_intent_list}
                ```
                
                ## <历史对话>
                ```
                {dao_sql.populate_chat_history()}
                ```
                
                ## <用户问题>: 
                {ask}
                
                
                最终只返回问题类别(不写解释)
                """,
            app_config.SELECTAI_PROFILE,
        )

    _logger.debug(f"### Intent determined(llm): {intent}")
    if intent != "其它类别":
        free_chat_intents = dao_sql.list_chat_intents()
        if intent not in free_chat_intents:
            vector_check = dao_sql.check_intent_distance(ask=ask, intent=intent)
            if not vector_check:
                intent = "其它类别"
    _logger.debug(f"### Intent determined(dbcheck): {intent}")

    ctx_intent = user_context.get_entry_val(user=user, entry_name="intent")
    _logger.debug(f"### ctx_intent: {ctx_intent}")

    if intent == "其它类别":
        state = user_context.get_entry_attr(
            user=user, entry_name="intent", attr_name="state"
        )
        if str(state).startswith("waiting_for_parameter"):
            intent = ctx_intent
    elif intent != ctx_intent:  # intent switched.
        user_context.set_entry(user=user, entry_name="intent", entry_value=intent)
        user_context.set_entry_attr(
            user=user, entry_name="intent", attr_name="state", attr_val=None
        )

    return intent


def extract_params(
    user: str, param_array: Optional[List[Dict[str, Any]]], ask: str, profile: str
) -> Dict[str, Any]:
    if not param_array:
        return None

    param_prompt_str = ""
    for p in param_array:
        pname = p["name"]
        plabel = p["label"]
        param_prompt_str = (
            f"{param_prompt_str}\n{pname}: 用户问题中提到的{plabel}是什么"
        )

    paras_extracted = selectai_util.chat(
        user=user,
        sentence=f"""
            ## INSTRUCTION
            你是一个参数提取能手，能按要求从 用户问题 中提取指定的参数，要求如下：
            1. 提取的参数需要与以下对应的列表作忽略大小写的精准匹配，并返回对应列表中的最匹配的一个值或空值。
            2. 注意用户问题中 YIELD, LOSS不是参数。
            3. 最终仅返回JSON对象格式，不需要其它任何的解释和文字或字符。
            
            ## 公司名称列表：
            {dao_sql.list_companies(), "所有公司", "全部公司"}
            
            ## 工厂名称列表：
            {dao_sql.list_factories(), "所有工厂", "全部工厂"}
            
            ## 产品名称列表：
            {dao_sql.list_products(), "所有产品", "全部产品"}
            
            ## 等级列表：
            {dao_sql.list_grades(), "所有等级", "全部等级"}
            
            ## 用户问题：{ask}
            
            ## 需要提取的参数：{param_prompt_str}

            
            最终只返回以下格式的JSON对象(不写解释):
            {{
                "param1": "param1's value", 
                "param2": "param2's value",
                ...
            }}
            """,
        llm_profile=profile,
        debug=False,
    )

    _logger.debug(f"### Params extracted: \n{paras_extracted}")
    paras_extracted = paras_extracted[
        next(idx for idx, c in enumerate(paras_extracted) if c in "{") :
    ].replace("```", "")

    cur_param_json = json.loads(paras_extracted)
    pre_param_json = user_context.get_entry_attr(
        user=user, entry_name="intent", attr_name="params"
    )
    param_json = {} if pre_param_json is None else dict(**pre_param_json)
    for n in cur_param_json:
        para_str_val = str(cur_param_json[n])
        if cur_param_json[n] is not None and len(para_str_val) > 0:
            if (
                para_str_val.startswith("所有") or para_str_val.startswith("全部")
            ) and n in param_json:
                del param_json[n]
            else:
                param_json[n] = cur_param_json[n]

    user_context.set_entry_attr(
        user=user, entry_name="intent", attr_name="params", attr_val=param_json
    )

    _logger.debug(
        f"### Params accumulated: \n {json.dumps(obj=param_json,ensure_ascii=False,indent=4)}"
    )

    return param_json


def search_data(user: str, ask: str):
    intent = determine_intent(user, ask)
    if intent == "其它类别":
        msg = "由于系统设定，我只能回答监督问题列表中的问题。如果您确定此问题需要纳入监督问题列表，请联系管理员。"
        _logger.debug(f"### Your query is not in the supervised question list: {ask}")
        return [{"content": msg, "source": "system", "score": 1}]
    elif intent == "批评语":
        msg = f"""非常抱歉，没能解决您的问题。作为一个智能助手，我会持续学习，尽快达到您的要求。在此之前，您可以问我如下这些主题的数据查询：
            {dao_sql.list_selectai_intents()}"""
        _logger.debug(f"### Your query is not in the supervised question list: {ask}")

    selectai_prompt, params = dao_sql.get_selectai_prompt_by_intent(intent)
    (chart, data_cols, name_cols, ext_rpt_url) = dao_sql.get_chart_by_intent(intent)

    if not selectai_prompt:
        chat_response = selectai_util.free_chat(user, ask, app_config.SELECTAI_PROFILE)
        return [{"content": chat_response, "source": "selectai", "score": 1}]

    param_array = None if not params else json.loads(params)
    if param_array is None:
        # No parameters for the intent.
        selectai_prompt_sentence = selectai_prompt.replace("$conditions", "")
    else:
        # Handle parameters for the intent.
        jparams = extract_params(user, param_array, ask, app_config.SELECTAI_PROFILE)

        missed_params = [
            para["label"]
            for para in param_array
            if para["required"] == "true" and para["name"] not in jparams
        ]

        if missed_params:
            user_context.set_entry_attr(
                user=user,
                entry_name="intent",
                attr_name="state",
                attr_val=f"waiting_for_parameter:required",
            )
            msg = f"您还需要提供如下参数：{'，'.join(missed_params)}"
            _logger.debug(f"### Asking for required parameter: {missed_params}")
            return [{"content": msg, "source": "system", "score": 1}]
        else:
            user_context.set_entry_attr(
                user=user,
                entry_name="intent",
                attr_name="state",
                attr_val=f"waiting_for_parameter:optional",
            )
            _logger.debug(f"### Changing parameters are allowed.")

        conditions = None
        for para in param_array:
            pname: str = para["name"]
            if pname in jparams and jparams[pname]:
                pprompt: str = para["prompt"]
                pprompt = pprompt.replace(f"<{pname}>", jparams[pname])
                conditions = (
                    f"{pprompt}" if not conditions else f"{conditions}，{pprompt}"
                )

        if conditions:
            conditions = f"，条件为：{conditions}"
            selectai_prompt_sentence = selectai_prompt.replace(
                "$conditions", conditions
            )
        else:
            selectai_prompt_sentence = selectai_prompt.replace("$conditions", "")

    _logger.debug(f"### SelectAI prompt: {selectai_prompt_sentence}")

    if result_cache.exists_entry(f"{user}_{selectai_prompt_sentence}"):
        _logger.debug(f"### Cache hit(GOOD): {selectai_prompt_sentence}")
        return result_cache.get_entry(f"{user}_{selectai_prompt_sentence}")

    request_id = uuid.uuid4().hex
    (query_json, query_rows, col_headers) = selectai_util.runsql(
        user, selectai_prompt_sentence, app_config.SELECTAI_PROFILE, request_id
    )

    search_result_object = (
        selectai_prompt_sentence,
        "",
        query_json,
        query_rows,
        col_headers,
        chart,
        data_cols,
        name_cols,
        ext_rpt_url,
    )

    if query_json and query_json[0] != "NO_DATA_FOUND":
        result_cache.set_entry(
            entry_name=f"{user}_{selectai_prompt_sentence}",
            entry_value=search_result_object,
        )
    return search_result_object


def execute_query(user: str, ask: str):
    search_result = search_data(user, ask)
    if len(search_result) == 1:
        return search_result

    (
        selectai_prompt_sentence,
        sql_sentence,
        query_json,
        query_rows,
        col_headers,
        chart,
        data_cols,
        name_cols,
        ext_rpt_url,
    ) = search_result

    if query_json == None:
        msg = "ChatBI助手目前还不能将您的这个问题转化为数据查询，请将这个问题反馈给系统管理员。"
        _logger.debug(f"### {msg}: {ask}")
        return [{"content": msg, "source": "system", "score": 1}]

    if query_json[0] == "NO_DATA_FOUND":
        msg = "根据您的问题，没有找到符合条件的数据或者您没有权限访问相关的数据。"
        _logger.debug(f"### {msg}: {ask}")
        return [{"content": msg, "source": "system", "score": 1}]

    if query_rows and len(query_rows) == 1 and len(query_rows[0]) == 1:
        chat_response = util_funcs.format_response_to_list(query_json)
    else:
        chat_response = util_funcs.format_response_to_table(query_json)
    if chart:
        chart_data = []
        if data_cols and name_cols:
            cols = [int(c.strip()) for c in data_cols.split(",")]
            names = [int(c.strip()) for c in name_cols.split(",")]
        else:
            cols = []
            names = []
        for col in cols:
            idx = cols.index(col)
            name_col = names[idx]
            chart_data.append(
                {
                    "title": col_headers[col],
                    "data": [str(d[col]).replace("%", "") for d in query_rows],
                    "name": [str(d[name_col]) for d in query_rows],
                }
            )
        chart_id = "chart_" + uuid.uuid4().hex
        chart_section = f"""<div data-for="gen_chart" onclick="{chart}{chart_id, chart_data}">...</div>
            <div class="chart_section" id="{chart_id}"></div>"""
    else:
        chart_section = ""

    user_question = f'<div class="user_question_section">问题复述：{selectai_prompt_sentence.split("。（")[0].split("？（")[0]}</div>'
    bot_answer = f'<div class="bot_answer_section">AI 回答：<br>{chat_response}</div>'

    if ext_rpt_url:
        ext_rpt_section = f'<div class="ext_report_section"><iframe src="{ext_rpt_url}"></iframe></div>'
    else:
        ext_rpt_section = ""

    return [
        {
            "content": user_question + bot_answer + chart_section + ext_rpt_section,
            "source": "selectai",
            "score": 1,
            "sql": sql_sentence,
        }
    ]
