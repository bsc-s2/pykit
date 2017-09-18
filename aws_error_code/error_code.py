import os

import yaml

dir_name = os.path.dirname(__file__)
file_name = os.path.join(dir_name, 'error_code.yaml')

with open(file_name, 'r') as f:
    file_content = f.read()

error_code = yaml.safe_load(file_content)
