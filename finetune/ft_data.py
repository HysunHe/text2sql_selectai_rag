import json
import sys
import os

path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
print(f"Path: {path}")
if not path in sys.path:
    sys.path.insert(1, path)
del path


input = "查询符合条件的各YIELD小等级占比（即YIELD_QTY之和/OUT_QTY之和），条件为：公司名称为COMPANY1，工厂名称为FACTORYNAME1，产品名称为PRODUCT1。占比用百分比表示并排序，用中文别名返回。"
prompt = """
[
  {
    "role" : "SYSTEM",
    "content" :
    [
      {
        "type" : "TEXT",
        "text" : "### Oracle SQL tables with their properties:"
      }
    ]
  },
  {
    "role" : "SYSTEM",
    "content" :
    [
      {
        "type" : "TEXT",
        "text" : "# CREATE TABLE \"HYSUN\".\"HKE_PROD_DEFECT\" (\"COMPANY\" VARCHAR2(50) '公司名称', \"NEW_OLD_PRODUCT\" VARCHAR2(50) '新旧标记', \"OUT_QTY\" NUMBER '产出数量', \"DEFECT_QTY\" NUMBER '缺陷数量', \"DEFECTDESC\" VARCHAR2(50) '缺陷描述', \"PANELDEFECTCODE\" VARCHAR2(50) '缺陷代码', \"PANELGRADE\" VARCHAR2(50) '面板等级', \"FACTORYNAME\" VARCHAR2(100) '工厂名称', \"PRODUCT\" VARCHAR2(50) '产品名称', \"TIMEVALUE\" NUMBER '时间数值', \"TIMEFLAG\" VARCHAR2(1) '时间标记')"
      }
    ]
  },
  {
    "role" : "SYSTEM",
    "content" :
    [
      {
        "type" : "TEXT",
        "text" : "# CREATE TABLE \"HYSUN\".\"HKE_PROD_OUT_YIELD_QTY\" (\"COMPANY\" VARCHAR2(50) '公司名称', \"NEW_OLD_PRODUCT\" VARCHAR2(50) '新旧标记', \"YIELD_QTY\" NUMBER '合格数量', \"OUT_QTY\" NUMBER '产出数量', \"GRADE\" VARCHAR2(50) '等级', \"FACTORYNAME\" VARCHAR2(100) '工厂名称', \"PRODUCT\" VARCHAR2(50) '产品名称', \"TIMEVALUE\" NUMBER '时间数值', \"TIMEFLAG\" VARCHAR2(1) '时间标记')"
      }
    ]
  },
  {
    "role" : "USER",
    "content" :
    [
      {
        "type" : "TEXT",
        "text" : "\n\nGiven an input Question, create a syntactically correct Oracle SQL query to run. \n - Pay attention to using only the column names that you can see in the schema description.\n - Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.\n - Please double check that the SQL query you generate is valid for Oracle Database.\n - Consider table name, schema name and column name to be case sensitive and enclose in double quotes.  - Only use the tables listed below. \n - If the table definition includes the table owner, you should include both the owner name and user-qualified table name in the Oracle SQL. - DO NOT keep empty lines in the middle of the Oracle SQL.\n - DO NOT write anything else except the Oracle SQL.\n - Always use table alias and easy to read column aliases. \n\nFor string comparisons in WHERE clause, CAREFULLY check if any string in the question is in DOUBLE QUOTES, and follow the rules: \n - If a string is in DOUBLE QUOTES, use case SENSITIVE comparisons with NO UPPER() function.\n - If a string is not in DOUBLE QUOTES, use case INSENSITIVE comparisons by using UPPER() function around both operands of the string comparison.\nNote: These rules apply strictly to string comparisons in the WHERE clause and do not affect column names, table names, or other query components.\n\nQuestion: '查询符合条件的各YIELD小等级占比（即YIELD_QTY之和/OUT_QTY之和），条件为：公司名称为COMPANY1，工厂名称为FACTORYNAME1，产品名称为PRODUCT1。占比用百分比表示并排序，用中文别名返回。'"
      }
    ]
  }
]
"""
sql = """
SELECT 
  "GRADE" AS "等级",
  ROUND(SUM("YIELD_QTY") / SUM("OUT_QTY") * 100, 2) AS "占比"
FROM 
  "HYSUN"."HKE_PROD_OUT_YIELD_QTY"
WHERE 
  UPPER("COMPANY") = UPPER('COMPANY1')
  AND UPPER("FACTORYNAME") = UPPER('FACTORYNAME1')
  AND UPPER("PRODUCT") = UPPER('PRODUCT1')
GROUP BY 
  "GRADE"
ORDER BY 
  "占比" DESC
"""

items = []
items.append(
    {
        "instruction": input,
        "input": "",
        "output": sql,
    }
)

with open("aireport.json", "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=4)
