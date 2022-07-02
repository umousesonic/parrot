# Parrot core module loader
# About colors:
# https://warehouse-camo.ingress.cmh1.psfhosted.org/953f08593d6a644522eec2a4fdc1966dacd4412d/68747470733a2f2f6769746c61622e636f6d2f64736c61636b772f696d616765732f7261772f6d61737465722f636f6c6f7265642f3235365f636f6c6f72735f66672e706e67
import os
import yaml
import logging
import importlib
from colored import fg, attr
from collections import namedtuple


VERSION = '0.1.1'

CommandEntry = namedtuple('CommandEntry', ['command', 'function'])
ModuleEntry = namedtuple('ModuleEntry', ['name', 'module', 'available_commands'])


class App:
    def __init__(self) -> None:
        print('Parrot core starting...')

        self.modules = []
        self.command_table = []
        self.terminating = False
        self.active_module = None

        # Load module
        self.load_modules()

    def load_modules(self):
        try:
            # Go through all folders under modules
            module_dirs = [d for d in os.listdir(os.path.join(os.getcwd(), 'modules')) if os.path.isdir(os.path.join(os.path.join(os.getcwd(), 'modules'), d))]

            # Go through each module's folder and see if module.yml exists
            for item in module_dirs:
                files = [f for f in os.listdir(os.path.join(os.path.join(os.getcwd(), 'modules'), item)) if os.path.isfile(os.path.join(os.path.join(os.path.join(os.getcwd(), 'modules'), item), f))]
                if 'module.yml' in files:
                    # Parse config
                    with open(os.path.join(os.path.join(os.path.join(os.getcwd(), 'modules'), item), 'module.yml')) as f:
                        data = yaml.safe_load(f)

                        # Module info
                        m_name = data['name']
                        m_version = data['version']
                        m_author = data['author']

                        print(f"[+] Found module {m_name} by {m_author}, {m_version}")

                        # Load module
                        module = importlib.import_module('modules.' + str(item) + '.' + m_name)

                        # Load available commands
                        this_module_command_entry = []
                        for cmd_pair in data['available_commands']:
                            this_module_command_entry.append(CommandEntry(list(cmd_pair.keys())[0], getattr(module, cmd_pair.get(list(cmd_pair.keys())[0]))))

                        # Register in module list
                        self.modules.append(ModuleEntry(m_name,
                                                        module,
                                                        this_module_command_entry))

        except Exception as e:
            print(f"%sError loading config file: {e}%s" % (fg(11), attr(0)))

    def register_command(self, command, function):
        self.command_table.append(CommandEntry(command, function))

    def execute_command(self, command):
        entry = [c for c in self.command_table if c.command == command[0]]
        if len(entry) == 0:
            print(f'%sNo such command: {command[0]}%s' % (fg(141), attr(0)))
            raise AttributeError
        return entry[0].function(command[1:])

    def shell(self):
        # Print splash screen
        print(f"%s * Parrot {VERSION} by Tianshu Wei %s" % (fg(14), attr(0)))
        print("%s * Welcome to Parrot shell!%s" % (fg(14), attr(0)))

        # Initialization
        self.register_internal_commands()

        # Shell main loop
        while not self.terminating:
            # Print line head and get user input
            breadcrumb = ''
            if self.active_module is not None:
                breadcrumb = f'\{self.active_module.name}'
            user_input = input(f"Parrot{breadcrumb}> ")

            # Process user input
            user_input = user_input.replace('\t', ' ')
            if user_input.isspace() or len(user_input) == 0:
                continue
            command = user_input.split(' ')

            # Execute command
            try:
                self.execute_command(command)
            except Exception as e:
                continue


    def register_internal_commands(self):
        self.register_command('exit', self.exit_shell)
        self.register_command('version', self.version)
        self.register_command('use', self.use_module)
        self.register_command('unload', self.unload)

    def exit_shell(self, args):
        self.terminating = True
        print('Bye...')

    def version(self, args):
        print(VERSION)

    def use_module(self, args):
        # Get module name and search that module
        module_name = args[0]
        get_modules = [m for m in self.modules if m.name == module_name]
        if len(get_modules) == 0:
            print("Not found!")
            return

        # Get module's body
        module = get_modules[0]

        # Register commands
        for item in module.available_commands:
            self.register_command(item.command, item.function)

        # Set active module
        self.active_module = module

    def unload(self, args):
        # Must be executed with an active module
        if self.active_module is None:
            return

        # Clear commands from table
        for item in self.active_module.available_commands:
            self.command_table.remove(item)

        # Set active module to none
        self.active_module = None


# Shell test utilities
# Will remove eventually
def print_hello(args):
    print('hello')

def test_echo(args):
    out_args = ' '.join(args)
    print(f'args: {out_args}')


if __name__ == '__main__':
    logging.getLogger().setLevel('INFO')
    app = App()
    app.register_command('hl', print_hello)
    app.register_command('te', test_echo)
    app.shell()