import yaml

with open('pykit/aws_error_codes/error_codes.yaml', 'r') as f:
    file_content = f.read()

error_codes = yaml.load(file_content)
