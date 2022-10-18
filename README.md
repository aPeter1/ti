# ideat
A command line interface for quickly recording ideas or notes while working in the terminal.

### Getting Started
##### Installation
You can install terminal idea with pip like so

`pip install ideat`

##### Configuration
Once you have `ideat` installed you will want to set up the configuration which can be done with the following command.

`ideat config <path-to-configuration-file>`

Typical `ti` usage would be something like `ideat log ideas 'build a weird idea recording app'` which in turn would log the 
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
Once your configuration is set, you can begin using `ideat`! 