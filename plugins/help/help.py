import os
import json

PLUGIN_DIR = os.getcwd()  + '/plugins'

def process_message(data):
    """
    Parse incoming message for help command
    """
    if 'text' in data.keys() and data['text'].startswith('pobo help'):

        cmd_dict = get_command_dict()

        if data['text'].split('pobo help')[1]:
            # Show all sub-commands for a top level command
            try:

                cmd = data['text'].split('pobo help')[1].strip()
                output = '*REFERENCE FOR %s COMMAND*\n_%s_\n\n' % (cmd.upper(), cmd_dict[cmd]['description'] )
                
                for sub_cmd in cmd_dict[cmd]['commands']:
                    output += '*%s*\t%s\n' % (sub_cmd['name'], sub_cmd['description'])            

            except KeyError:
                error = '_Sorry,_ `%s` _is a bogus command, or I have no help file for it._' % cmd
                return outputs.append([data['channel'], error])                        

            output += '\n_Syntax:_ `pobo %s <command>`\n_Example:_ `pobo %s`' % (cmd, cmd_dict[cmd]['example'])

            # If this command has an "abbreviated" form, add info about it to help output
            if 'abbrev' in cmd_dict[cmd].keys():
                output += '\n\n*PROTIP:* Save your fingers, this command has abbrevation. Try typing `%s<command>` instead of `pobo %s <command>`' % (cmd_dict[cmd]['abbrev'], cmd )

        else:        
            # Show all top level commands
            output = '*POBO COMMANDS*\n_All the weird things pobo can do._\n\n'
            for key, value in cmd_dict.iteritems():
                output += '*%s*\t%s\n' % (value['name'], value['description'])
            
            output += '\n_Type_ `pobo help <command>` _to see options for each command._\n'
        
        outputs.append([data['channel'], output])

def get_command_dict():
    """
    Check all plugin folders for a file called help.json. Build a dict of commands
    based on these help files.
    """
    command_dict = {}

    for dir in os.walk(PLUGIN_DIR):
        if 'help.json' in dir[2]:

            help_file = open('%s/help.json' % dir[0]).read()
            help_dict = json.loads(help_file)
            command_dict[ help_dict['name'] ] = help_dict

    return command_dict


