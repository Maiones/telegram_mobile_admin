#!/bin/bash

#pgrep -f "bot_9.py"

script1=bot_9.py
directory1="/home/user/kva-kva/scripts/python"

if ! pgrep -f "$script1" >/dev/null
then
    echo "Script is not running, restarting..."
    source $directory1/moo_bot/bin/activate && python3 $directory1/$script1 &
else
    echo "Script is running"
fi

exit 0