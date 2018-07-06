#!/bin/bash
# Run daemon in the background, send commands using the client and wait for the daemon to
# finish downloading all data.
#
# To run this script you must have a client commands file, and set the relevant variables below.
# All packages of TwitterNetwork must be available from the current working directory.

COMMANDS_FILE="client-commands"
SERVER_CONF="conf/server.conf"
CLIENT_CONF="conf/client.conf"

if [ ! -f "$COMMANDS_FILE" ] || [ ! -f "$SERVER_CONF" ] || [ ! -f "$CLIENT_CONF" ]; then
    echo "You must set the paths for the commands file and the config files inside this script"
fi

echo 'starting daemon'
python3 -m TwitterMine.daemon -c "$SERVER_CONF" -a app > /dev/null &
DAEMON_PID=$!

sleep 10 # wait for daemon to be ready

echo 'sending requests from client'
python3 -m TwitterMine.client -c "$CLIENT_CONF" -s "$COMMANDS_FILE" > client.out

echo 'sleep 5 minutes (let daemon digest all requests)'
sleep 300

echo 'sending shutdown request to daemon (daemon will shutdown after all the data was mined)'
echo 'server shutdown' | python3 -m TwitterMine.client -c "$CLIENT_CONF -i > /dev/null

echo 'waiting for daemon to finish...'
wait $DAEMON_PID

echo 'daemon finished. script ends'
