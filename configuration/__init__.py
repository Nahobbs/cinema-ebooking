import yaml

try:
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
except:
    with open('../config.yaml', 'r') as f:
        config = yaml.safe_load(f)
