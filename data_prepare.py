""" 
Description: 
 - Prepare the supervised question list. The AI assistant only
   handles those questions in the list.

History:
 - 2025/01/29 by Hysun (hysun.he@oracle.com): Initial version
"""

import time
import oracledb
from dao import db_pool
from aimodels import app_embedding

# 实际情况中，监督问题列表放到数据库表中进行动态删减和编辑，可以用APEX快速开发一个管理界面进行管理和维护。
SUPERVISED_QUESTIONS = [
    {"intent": "问候语"},
    {"intent": "赞美语", "examples": ["你太棒了"]},
    {"intent": "批评语", "examples": ["啥玩意"]},
    {
        "intent": "YIELD小等级占比",
        "selectai_prompt": """查询符合条件的各YIELD等级占比（计算方法：YIELD_QTY之和/OUT_QTY之和）$conditions（占比以百分比表示并保留两位小数，返回等级和占比两列）""",
        "ext_report_url": "https://slurm.hysun.cloudns.asia/hke-ext/test.html?title=YIELD小等级占比",
        "chart_type": "bar",
        "chart_data_cols": "1",
        "chart_name_cols": "0",
        "params": """[{
            "name": "COMPANY_NAME",
            "required": "true",
            "prompt": "公司名称为<COMPANY_NAME>",
            "label": "公司名称"
        }, {
            "name": "FACTORY_NAME",
            "required": "true",
            "prompt": "工厂名称为<FACTORY_NAME>",
            "label": "工厂名称"
        }, {
            "name": "PRODUCT_NAME",
            "required": "true",
            "prompt": "产品名称为<PRODUCT_NAME>",
            "label": "产品名称"
        }]""",
        "examples": ["YIELD小等级占比"],
    },
    {
        "intent": "LOSS小等级占比",
        "selectai_prompt": """查询缺陷产品的各等级占比（计算方法：DEFECT_QTY之和/OUT_QTY之和）$conditions（占比以百分比表示并保留两位小数，返回等级和占比两列）""",
        "ext_report_url": "https://slurm.hysun.cloudns.asia/hke-ext/test.html?title=LOSS小等级占比",
        "chart_type": "bar",
        "chart_data_cols": "1",
        "chart_name_cols": "0",
        "params": """[{
            "name": "COMPANY_NAME",
            "required": "true",
            "prompt": "公司名称为<COMPANY_NAME>",
            "label": "公司名称"
        }, {
            "name": "FACTORY_NAME",
            "required": "true",
            "prompt": "工厂名称为<FACTORY_NAME>",
            "label": "工厂名称"
        }, {
            "name": "PRODUCT_NAME",
            "required": "true",
            "prompt": "产品名称为<PRODUCT_NAME>",
            "label": "产品名称"
        }, {
            "name": "GRADE",
            "required": "false",
            "prompt": "等级为<GRADE>",
            "label": "等级"
        }]""",
        "examples": ["LOSS小等级占比"],
    },
    {
        "intent": "不良排名",
        "selectai_prompt": """按公司、工厂和产品分组统计不良排名$conditions（返回公司名称、工厂名称、产品名称、不良数量和不良率五列，不良率用百分比表示并取两位小数，结果按不良率排序显示）""",
        "ext_report_url": "https://slurm.hysun.cloudns.asia/hke-ext/test.html?title=不良排名",
        "params": """[{
            "name": "COMPANY_NAME",
            "required": "false",
            "prompt": "公司名称为<COMPANY_NAME>",
            "label": "公司名称"
        }, {
            "name": "FACTORY_NAME",
            "required": "false",
            "prompt": "工厂名称为<FACTORY_NAME>",
            "label": "工厂名称"
        }, {
            "name": "PRODUCT_NAME",
            "required": "false",
            "prompt": "产品名称为<PRODUCT_NAME>",
            "label": "产品名称"
        }]""",
        "examples": ["不良排名"],
    },
    {
        "intent": "良率统计",
        "selectai_prompt": """按产品名称分组查询各产品综合良率$conditions（返回产品名称和综合良率两列，其中综合良率以百分比表示并保留两位小数）""",
        "ext_report_url": "https://slurm.hysun.cloudns.asia/hke-ext/test.html?title=良率系统览",
        "chart_type": "pie",
        "chart_data_cols": "1",
        "chart_name_cols": "0",
        "params": """[{
            "name": "COMPANY_NAME",
            "required": "false",
            "prompt": "公司名称为<COMPANY_NAME>",
            "label": "公司名称"
        }, {
            "name": "FACTORY_NAME",
            "required": "false",
            "prompt": "工厂名称为<FACTORY_NAME>",
            "label": "工厂名称"
        }, {
            "name": "PRODUCT_NAME",
            "required": "false",
            "prompt": "产品名称为<PRODUCT_NAME>",
            "label": "产品名称"
        }]""",
        "examples": ["良率系统概览", "查询良率", "良率统计"],
    },
    {
        "intent": "不良分布",
        "selectai_prompt": """查询各等级的缺陷总数量$conditions（按缺陷总数量倒序显示并返回等级和缺陷总数量两列）""",
        "ext_report_url": "https://slurm.hysun.cloudns.asia/hke-ext/test.html?title=不良等级分布趋势图",
        "chart_type": "bar",
        "chart_data_cols": "1",
        "chart_name_cols": "0",
        "params": """[{
            "name": "COMPANY_NAME",
            "required": "false",
            "prompt": "公司名称为<COMPANY_NAME>",
            "label": "公司名称"
        }, {
            "name": "FACTORY_NAME",
            "required": "false",
            "prompt": "工厂名称为<FACTORY_NAME>",
            "label": "工厂名称"
        }, {
            "name": "PRODUCT_NAME",
            "required": "false",
            "prompt": "产品名称为<PRODUCT_NAME>",
            "label": "产品名称"
        }]""",
        "examples": ["不良等级分布", "查询不良分布"],
    },
]


start = time.perf_counter()

print("### Deleting existing data...")

with db_pool.vectordb_pool.acquire() as connection:
    with connection.cursor() as cursor:
        cursor.execute("truncate table HKE_SUPERVISED_QUESTIONS")
        cursor.execute("truncate table HKE_QUESTION_EXAMPLES")

print("### Existing data deleted. Now building new data...")

for question in SUPERVISED_QUESTIONS:
    intent = question.get("intent")
    intent_vector = app_embedding.embedding_model.embed_documents([intent])[0]
    prompt = question.get("selectai_prompt")
    profile = question.get("selectai_profile")
    ext_url = question.get("ext_report_url")
    sql_text = str(question.get("sql_text")).strip() if "sql_text" in question else ""
    chart_type = (
        str(question.get("chart_type")).strip() if "chart_type" in question else ""
    )
    chart_data_cols = (
        str(question.get("chart_data_cols")).strip()
        if "chart_data_cols" in question
        else ""
    )
    chart_name_cols = (
        str(question.get("chart_name_cols")).strip()
        if "chart_name_cols" in question
        else ""
    )

    params = str(question.get("params")).strip() if "params" in question else ""

    examples = question.get("examples")
    embeddings = None
    if examples:
        embeddings = app_embedding.embedding_model.embed_documents(list(examples))

    with db_pool.vectordb_pool.acquire() as connection:
        default_autocommit = connection.autocommit
        connection.autocommit = False
        with connection.cursor() as cursor:
            cursor.setinputsizes(
                oracledb.DB_TYPE_VARCHAR,
                oracledb.DB_TYPE_VARCHAR,
                oracledb.DB_TYPE_VARCHAR,
                oracledb.DB_TYPE_VARCHAR,
                oracledb.DB_TYPE_VARCHAR,
                oracledb.DB_TYPE_VARCHAR,
                oracledb.DB_TYPE_VARCHAR,
                oracledb.DB_TYPE_VARCHAR,
                oracledb.DB_TYPE_VARCHAR,
                oracledb.DB_TYPE_VECTOR,
            )
            cursor.execute(
                "INSERT INTO HKE_SUPERVISED_QUESTIONS (INTENT, SELECTAI_PROMPT, SELECTAI_PROFILE, SQL_TEXT, CHART_TYPE, CHART_DATA_COLS, CHART_NAME_COLS, EXT_REPORT_URL, PARAMS, INTENT_EMBEDDING) VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10)",
                (
                    intent,
                    prompt,
                    profile,
                    sql_text,
                    chart_type,
                    chart_data_cols,
                    chart_name_cols,
                    ext_url,
                    params,
                    str(intent_vector),
                ),
            )
        if embeddings:
            with connection.cursor() as cursor:
                cursor.setinputsizes(
                    oracledb.DB_TYPE_VARCHAR,
                    oracledb.DB_TYPE_VARCHAR,
                    oracledb.DB_TYPE_VECTOR,
                )
                cursor.executemany(
                    "INSERT INTO HKE_QUESTION_EXAMPLES (INTENT, EXAMPLE_QUESTION, QUESTION_EMBEDDING) VALUES (:1, :2, :3)",
                    list(
                        zip(
                            [intent for _ in examples],
                            examples,
                            [str(e) for e in embeddings],
                        )
                    ),
                )
        connection.commit()
        connection.autocommit = default_autocommit

end = time.perf_counter()
print(f"### Done. Total elapsed seconds: {round(end - start, 3)}")
