#!/bin/bash
# اجرای هارنس + تست اندپوینت‌ها در یک اسکریپت
cd /home/z/my-project/tests/tmp
pkill -f agent_harness.py 2>/dev/null
sleep 0.5
python3 agent_harness.py > harness_v12.log 2>&1 &
HPID=$!
sleep 4
python3 test_endpoints_v12.py
EXIT=$?
kill $HPID 2>/dev/null
wait $HPID 2>/dev/null
exit $EXIT
