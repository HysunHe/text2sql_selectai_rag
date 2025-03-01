# 介绍

AiReport Project。

## Python版本

运行该程序需要 Python 3.12。例如，可以使用 conda 或 poetry 创建一个 python 虚拟环境：

conda create -n aireport python=3.12

## Python包依赖

pip install -r requirements.txt

## 环境变量配置

服务启动时，会从文件 app.env 中读取环境变量信息。

## 启动程序

start.sh: 启动或重启。如果程序已经在运行，那么运行start.sh时将先杀掉正在运行的进程，再启动新的进程。

## GUI

https://wdsshsl4d6foyhp-cntech.adb.ap-chuncheon-1.oraclecloudapps.com/ords/r/hys/chatbi185/home (demo/Demo123#)

## Demo script

YIELD小等级占比：
对话流程：
1. 输入 “查询company1公司生产的product1产品各YIELD小等级占比”
2. 请提供您需要查询的工厂名称？===> 输入“factoryname1”
3. 继续输入 “company2公司生产的product2呢”
4. 完成对话。


不良排名：
对话流程：
1. 输入 “显示不良排名”
2. 继续输入 “只显示company1公司的”
3. 继续输入 “只显示product1的”
3. 继续输入 “只显示product2的”