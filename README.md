# TwitterMine

TwitterMine extracts data from twitter.com (Twitter) and saves it 
locally. Since Twitter limits the number of its API calls, pulling
large amount of data from twitter can take a long time. 
TwitterMine provides a service that can run in the background 
(daemon) and constantly talk to Twitter's API and download 
desired information, under the API limits. It also consist of a 
client through which requests can be easily forwarded to the 
daemon to handle.


TwitterMine depends on a forked version of TwitterAPI, so be sure to get the correct version which
is linked here as a sub-module (installing TwitterAPI via pip for example will not be compatible).  
An easy way to set things up is to download the [release tarball](https://github.com/jonahar/TwitterMine/releases/download/v0.1/TwitterMine-v0.1.tar) and run TwitterMine
modules from the top directory using python's `-m` flag.


## Daemon
The daemon reads its required arguments from the config file
which is json formatted. The daemon requires Twitter's app keys and access tokens
(see [https://apps.twitter.com/](https://apps.twitter.com/)). To 
find all required arguments check the `server.conf` template.  
After setting up the config file the daemon can be started by
running

`python3 -m TwitterMine.daemon -c <config_file>`

or display the help menu:

`python3 -m TwitterMine.daemon -h`


## Client

The client should be configured with the daemon host and port (see `client.conf` template). config file should be given through the `-c` flag.  
The client can run in two modes:
- interactive mode - commands are read from the user via the terminal. Use with `-i` flag
- script mode - commands are read from a file, each command in a new line. Use with `-s <script>` flag

Obviously, help menu can be displayed with `python3 -m TwitterMine.client -h`

