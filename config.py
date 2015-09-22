"""
    
    ~~~
    
    By: Alex on 9/18/2015
"""
__author__ = 'Alex'
import json, os

class Watched(object):
    def __init__(self):
        self._observers = []

    def broadcast(self, **kwargs):
        for callback in self._observers:
            callback(**kwargs)

    def bind_to(self, callback):
        if callback not in self._observers:
            self._observers.append(callback)

    def unbind_from(self, callback):
        if callback in self._observers:
            self._observers.remove(callback)


class DynamicConfig(Watched):

    def __init__(self, **kwargs):
        super().__init__()
        self._file = kwargs.get("file", None)
        self._config = kwargs.get("default_config", {})

    def load(self, file=None):
        if self._file or file:
            if os.path.exists(file or self._file):
                with open(file or self._file) as json_file:
                    file_config = json.load(json_file)
                    if isinstance(self._config, list):
                        self._config = type(self._config)()
                    for item in file_config:
                        if isinstance(self._config, list):
                            self._config.append(item)
                        elif isinstance(self._config, dict):
                            if not str(item).startswith("^"):
                                self._config[item] = file_config[item]

    def save(self, file=None):
        if self._file or file:
            new_chunk = type(self._config)()
            for item in self._config:
                if isinstance(self._config, list):
                    new_chunk.append(item)
                elif isinstance(self._config, dict):
                    if not str(item).startswith("^"):
                        new_chunk[item] = self._config[item]
            with open(file or self._file, 'w+') as json_file:
                json.dump(new_chunk, json_file, indent=4, sort_keys=True)


class DynamicConfigDict(DynamicConfig):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __getitem__(self, key):
        return self.get_value(key)

    def __setitem__(self, key, value):
        self.set_value(key, value)

    def set_value(self, key, value):
        self._config[key] = value
        for callback in self._observers:
            callback(key, value)

    def get_value(self, key):
        key = str(key).replace('^', '')
        return self._config[key] if key in self._config.keys() else None


class DynamicConfigList(DynamicConfig):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._config = kwargs.get("default_config", [])

    def append(self, item):
        for callback in self._observers:
            callback(item)
        return self._config.append(item)

    def __iter__(self):
        return iter(self._config)

    def __next__(self):
        return next(self._config)

    def remove(self, item):
        print(item)
        return self._config.remove(item)

    def pop(self, item):
        return self._config.pop(item)