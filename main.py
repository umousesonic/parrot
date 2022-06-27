# Parrot core module loader
import os
import yaml
import logging


class App:
    def __init__(self) -> None:
        print('Parrot core starting...')
        # Load module
        self.load_modules

    
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

                        print(f"Found module {m_name} by {m_author}, {m_version}")


        except Exception as e:
            print(f"Error loading config file: {e}")




if __name__ == '__main__':
    logging.getLogger().setLevel('INFO')
    app = App()