import json

# load config file
with open('data/play/sample_dict.json') as f:
    sample_dict = json.load(f)

class DictData:
    class GenshinSample:
        dictionary: dict = sample_dict