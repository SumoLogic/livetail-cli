# Sumo Logic Live Tail Command Line Interface (CLI)

[![Join the chat at https://gitter.im/SumoLogic/livetail-cli](https://badges.gitter.im/SumoLogic/livetail-cli.svg)](https://gitter.im/SumoLogic/livetail-cli?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

The Live Tail Command Line Interface (CLI) is a standalone application that allows you to start and use a Live Tail session from the command line, similar to `tail -f`
The output is directed to stdout - so you can pipe the output to commands (grep, awk etc)

## Installation

[OSX binaries are provided for CLI. ] (https://github.com/SumoLogic/livetail-cli/releases)
Windows and Linux binaries coming up soon!!

Simply extract the archive and place the binaries to a location where you have read/write access. 

## Usage

Like [SumoLogic] (https://www.sumologic.com), the Live Tail CLI enables you to tail logs in real time by specifying a filter.
It uses accessId and accessKeys that are used with the SumoLogic API for authentication. 
You could either provide the credentials each time using -i and -k command line options, or enter them once when prompted and they would be saved locally in config.json file in the same directory as the CLI. 

The first time you run the CLI, the tool will prompt you to choose your deployment.
See [Help for the correct endpoint.] (https://service.sumologic.com/help/Default.htm#Sumo_Logic_Endpoints.htm)

## Examples

Tail all logs from a given Source Host. 
```
./livetail “_sourceHost = localhost”
```

Tail logs from a sourceCategory, grep for a pattern, write it to a file
```
./livetail “_sourceCategory = service” | grep -i “rate limit exceeded” > out.txt
```


Happy Tailing!

                            

