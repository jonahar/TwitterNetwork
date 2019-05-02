**TwitterNetwork** was created for representing and analyzing networks in Twitter. It consists of tools for 
mining data from Twitter and generating graphs out of the data (which can be visualized using 
external tools such as gephi).  
Its 2 main parts are TwitterMine and TwitterGraph.  
  
TwitterNetwork depends on a forked version of TwitterAPI, so be sure to get the correct version which
exists here as a submodule. The quickest way to set things up is to download the release tarball from the [Releases](https://github.com/jonahar/TwitterNetwork/releases) page.

**TwitterNetwork** was used in the work on [this post](https://medium.com/@avivzohar/the-cryptocurrency-filter-bubble-faa0901f0e0a).


## TwitterMine

TwitterMine extracts data from twitter.com (Twitter) and saves it 
locally. Since Twitter limits the number of its API calls, pulling
large amount of data from twitter can take a long time. 
TwitterMine provides a service that can run in the background 
(daemon) and constantly talk to Twitter's API and download 
desired information, under the API limits. It also consist of a 
client through which requests can be easily forwarded to the 
daemon to handle.


#### Daemon
The daemon reads its required arguments from the config file
which is json formatted. The daemon requires Twitter's app keys and access tokens
(see [https://apps.twitter.com/](https://apps.twitter.com/)). To 
find all required arguments check the `server.conf` template.  
After setting up the config file the daemon can be started by
running

`python3 -m TwitterMine.daemon -c <config_file>`

or display the help menu:

`python3 -m TwitterMine.daemon -h`


#### Client

The client should be configured with the daemon host and port (see `client.conf` template). config 
file should be given in the `-c` option.  
The client can run in two modes:
- interactive mode - commands are read from the user via the standard input. Use with `-i` flag
- script mode - commands are read from a file, each command in a new line. Use with `-s <script>` option

Run `python3 -m TwitterMine.client -h` to see the help menu and a list of all valid commands.



## TwitterGraph
This package is used for downloading data (using TwitterMine) and generate graph files. It has all 
necessary scripts that, when combined together, can create a complete and final graph files.


A typical workflow may be:

1. Filling all field in the `graph_properties.json` file

2. run search and create relevant client commands  

```
python3 -m TwitterGraph.search <graph-properties-file> comma,separated,search,terms
python3 -m TwitterGraph.create_commands_file <graph-properties-file>
```

3. start daemon and send all commands using the client

```
python3 -m TwitterMine.daemon [OPTIONS]
```
```
python3 -m TwitterMine.client -s <client-commands-file> -c <client-config-file>
```

4. When daemon finished downloading all required data, extract data from the data_dir and prepare
the necessary files for writing the graph files.

`python3 -m TwitterGraph.extract_data <graph-properties-file>`

5. Run MCL to find a clustering of the network and write the final gexf file

`python3 -m TwitterGraph.mcl_graph [OPTIONS]`
