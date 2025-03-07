
# Description: 
# - AiReport project. This is a demo POC project, it is not intented
#   for production. The quality of the code is not guaranteed. 
#   
#   If you refrence the code in this project, it means that you understand
#   the risk and you are responsible for any issues caused by the code.
#
# History:
# - 2025/01/20 by Hysun (hysun.he@oracle.com): Initial implementation.


kill -9 `lsof -i:8080 | awk '{print $2}' | grep -v "PID"` > /dev/null 2>&1

echo -n "Starting service ."

source `conda info --base`/etc/profile.d/conda.sh
conda activate base

nohup python main.py > /dev/null 2>&1 &

arg1=$1

log_file=$LOG_FILE_PATH

if [[ -z $log_file ]]
then
        log_file=`grep "LOG_FILE_PATH" app.env | sed  "s/LOG_FILE_PATH=//"`
fi

if [[ $arg1 != "nowait" ]]
then
        while true
        do
                result=`tail $log_file`
                if [[ $result == *"WSGI server listening at"* ]]; then
                        echo 'Service started.'
                        break
                else
                        echo -n '.'
                        sleep 1
                fi
        done
fi

cd - > /dev/null

echo "--------------"

echo "To view logs, run the command [ tail -300f $log_file ]"
