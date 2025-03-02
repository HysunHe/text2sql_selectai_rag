cd /home/ubuntu/Hysun/text2sql_selectai_rag
. app.env

kill -9 `lsof -i:8080 | awk '{print $2}' | grep -v "PID"` > /dev/null 2>&1

echo -n "Starting service ."

source `conda info --base`/etc/profile.d/conda.sh
conda activate base

nohup python main.py > /dev/null 2>&1 &

arg1=$1

if [[ $arg1 != "nowait" ]]
then
        while true
        do
                result=`tail $LOG_FILE_PATH`
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

echo "To view logs, run the command [ tail -300f $LOG_FILE_PATH ]"
