# ideat
A command line interface for quickly recording ideas or notes while working in the terminal.

### Getting Started
##### Installation
You can install terminal idea by running the install script

```commandline
$/bin/sh install.sh
```

##### Configuration
Once you have `ti` installed you will want to set up the configuration which can be done with the following command.

```commandline
$ ti config <path-to-configuration-file>
```

Typical `ti` usage would be something like `ti log ideas 'build a weird idea recording app'` which in turn would log the 
message 'build a weird idea recording app' to a file specified in your configuration for `ideas`. Such a configuration
file would look something like this:

```json
{
  "default": "ideas",
  "ideas": "ideas_log.txt"
}
```

You can set any subject as your `default` and if you specify no subject in your command, it will log there.

##### Usage
Once your configuration is set, you can begin using `ti`! 

```commandline
usage: ti [-h] [-v] {config,log,out,mark,unmark,del} ...

positional arguments:
  {config,log,out,mark,unmark,del}
    config              Set the config file
        positional arguments:
          file        Path of the configuration file

    log                 Log a message
        positional arguments:
          type        The type of message to log
          message     The message to log

    out                 Output all messages of type
        positional arguments:
            type        The type of message to output
        options:
            -s          Only output messages

    mark                Mark message(s) at index(s)
        positional arguments:
          type        The type of message to mark
          range       Index to mark or two to indicate a range
          
    unmark              Unmark message(s) at index(s)
        positional arguments:
          type        The type of message to unmark
          range       Index to unmark or two to indicate a range

    del                 Delete message(s) at index(s)
        positional arguments:
          type        The type of message to delete
          range       Index to delete or two to indicate a range

options:
  -h, --help            Show this help message and exit
  -v                    Enable verbose logging

```