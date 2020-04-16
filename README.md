# Sumo Logic Live Tail Command Line Interface (CLI)

[![Join the chat at https://gitter.im/SumoLogic/livetail-cli](https://badges.gitter.im/SumoLogic/livetail-cli.svg)](https://gitter.im/SumoLogic/livetail-cli?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

The Live Tail Command Line Interface (CLI) is a standalone application that allows you to start and use a Live Tail session from the command line, similar to `tail -f`.
The output is directed to stdout - so you can pipe the output to commands (grep, awk etc)

This feature is documented [here.](http://help.sumologic.com/Search/Live_Tail/Live_Tail_CLI)

## Installation

[Platform specific binaries are provided for CLI.](https://github.com/SumoLogic/livetail-cli/releases)

Simply extract the archive and place the binaries to a location where you have read/write access. 

## Source Code

The source code of the Live Tail CLI is included in this repository.

Prerequisites to use the script: 
 - Python 3
 - the `requests` library https://pypi.org/project/requests/.

## Usage

Like [SumoLogic](https://www.sumologic.com), the Live Tail CLI enables you to tail logs in real time by specifying a filter.
It uses accessId and accessKeys that are used with the SumoLogic API for authentication. 
You could either provide the credentials each time using -i and -k command line options, or enter them once when prompted and they would be saved locally in config.json file in the same directory as the CLI. 

Using the provided Access Id and Access Key, the script will be able to automatically determine a deployment where your account exists.

If you would like to use the Live Tail CLI with a Sumo internal deployment, please specify the deployment in the program arguments using the -d option as it cannot be determined automatically.

### Command Line Options

```
usage: livetail [-h] [-i ACCESSID] [-k ACCESSKEY] [-d DEPLOYMENT] [-v] [-c] [filter]

positional arguments:
  filter         Live Tail filter

optional arguments:
  -h, --help     show this help message and exit
  -i ACCESSID    Access ID
  -k ACCESSKEY   Acccess Key
  -d DEPLOYMENT  Deployment-specific Sumo Logic API URL e.g. api.sumologic.com
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
