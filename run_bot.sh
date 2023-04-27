#!/bin/bash

if ! pgrep -f "bot_9.py" >/dev/null
then
    echo "Script is not running, restarting..."
    su - user -c "source /home/user/kva-kva/scripts/python/moo_bot/bin/activate && python3 /home/user/kva-kva/scripts/python/bot_9.py &"
else
    echo "Script is running"
fi