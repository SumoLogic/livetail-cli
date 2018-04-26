# Sumo Logic Live Tail Command Line Interface (CLI)

[![Join the chat at https://gitter.im/SumoLogic/livetail-cli](https://badges.gitter.im/SumoLogic/livetail-cli.svg)](https://gitter.im/SumoLogic/livetail-cli?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

The Live Tail Command Line Interface (CLI) is a standalone application that allows you to start and use a Live Tail session from the command line, similar to `tail -f`
The output is directed to stdout - so you can pipe the output to commands (grep, awk etc)

This feature is documented [here.](http://help.sumologic.com/Search/Live_Tail/Live_Tail_CLI)

| TLS Deprecation Notice |
| --- |
| In keeping with industry standard security best practices, as of May 31, 2018, the Sumo Logic service will only support TLS version 1.2 going forward. Verify that all connections to Sumo Logic endpoints are made from software that supports TLS 1.2. |

## Installation

[Platform specific binaries are provided for CLI.](https://github.com/SumoLogic/livetail-cli/releases)

Simply extract the archive and place the binaries to a location where you have read/write access. 

## Usage

Like [SumoLogic](https://www.sumologic.com), the Live Tail CLI enables you to tail logs in real time by specifying a filter.
It uses accessId and accessKeys that are used with the SumoLogic API for authentication. 
You could either provide the credentials each time using -i and -k command line options, or enter them once when prompted and they would be saved locally in config.json file in the same directory as the CLI. 

The first time you run the CLI, the tool will prompt you to choose your deployment.
See [Help for the correct endpoint.](http://help.sumologic.com/Send_Data/Collector_Management_API/Sumo_Logic_Endpoints)

### Command Line Options

```
usage: livetail [-h] [-i ACCESSID] [-k ACCESSKEY] [-v] [-c] [filter]

positional arguments:
  filter         Live Tail filter

optional arguments:
  -h, --help     show this help message and exit
  -i ACCESSID    Access ID
  -k ACCESSKEY   Acccess Key
  -v, --version  show program's version number and exit
  -c             clear Live Tail
```

## Examples

Tail all logs from a given Source Host. 

```sh
./livetail “_sourceHost = localhost”
```

Tail logs from a sourceCategory, grep for a pattern, write it to a file

```sh
./livetail “_sourceCategory = service” | grep -i “rate limit exceeded” > out.txt
```

Happy Tailing!
