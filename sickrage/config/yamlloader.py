'''
Created on 6 jun. 2016

@author: RHELMER
'''

import logging
import os
import yaml
from yaml import YAMLError
import sickbeard

logger = logging.getLogger('yamlloader')


class MarkedYAMLError(YAMLError):
    def __init__(self, context=None, context_mark=None,
                 problem=None, problem_mark=None, note=None):
        self.context = context
        self.context_mark = context_mark
        self.problem = problem
        self.problem_mark = problem_mark
        self.note = note

    def __str__(self):
        lines = []
        if self.context is not None:
            lines.append(self.context)
        if self.context_mark is not None  \
           and (self.problem is None or self.problem_mark is None or
                self.context_mark.name != self.problem_mark.name or
                self.context_mark.line != self.problem_mark.line or
                self.context_mark.column != self.problem_mark.column):
            lines.append(str(self.context_mark))
        if self.problem is not None:
            lines.append(self.problem)
        if self.problem_mark is not None:
            lines.append(str(self.problem_mark))
        if self.note is not None:
            lines.append(self.note)
        return '\n'.join(lines)


class YamlLoader(object):
    '''
    Class for loading a yaml object using a yml config file location
    :param yaml_config: config file location. Filename should end with the extention .yml
    '''

    def __init__(self, yaml_config, callback=None):
        '''
        :param yaml_config: The yaml config filename, will be placed in DATA_DIR/config/
        :param callback: the object instance that's calling the yamlloader.
        This is used for initializing the yaml config, if the file doesn't exist
        '''
        self.config_dir = os.path.join(sickbeard.DATA_DIR, 'config')
        self.config_file = os.path.join(self.config_dir, yaml_config)
        self.data = None
        self.yaml_load = False
        self.yaml_parse = False
        self.callback = callback

        if not os.path.isfile(self.config_file):
            logger.error("Can't find yaml file location: [%s], creating new config %s in %s",
                         self.config_file, self.config_file, self.config_dir)
            new_data = self.new()
            if new_data:
                # Saving succeeded, we should got back a dict
                self.data = new_data
                self.yaml_load = True
                return

        try:
            f = open(self.config_file)
            txt = f.read()
        except IOError:
            logger.error("Error: can't find file or read data")
            return
        else:
            self.yaml_load = True
            logger.debug("Loaded config file %s successfully", self.config_file)
            f.close()

        try:
            self.data = yaml.load(txt, yaml.SafeLoader)
        except MarkedYAMLError as exc:
            logger.error("Error while parsing YAML file:")
            if hasattr(exc, 'problem_mark'):
                if exc.context is not None:
                    logger.error("Error when trying to load yaml config saying: "
                                 "%s\n %s %s\nPlease correct data and retry.", exc.problem_mark, exc.problem, exc.context)
                else:
                    logger.error(' parser says\n %s\n%s\nPlease correct data and retry.', exc.problem_mark, exc.problem)
            else:
                logger.error("Something went wrong while parsing yaml file")
                self.data = None
        else:
            self.yaml_parse = True

    def new(self):
        if not self.callback:
            return

        self.data = self.callback.init_config()
        self.save()
        return self.data

    def save(self, data=None):
        if data:
            self.data = data

        with open(os.path.join(self.config_file), 'w') as outfile:
            outfile.write(yaml.safe_dump(self.data, default_flow_style=False))

#yaml_test = YamlLoader('provider.yml')
#pass
