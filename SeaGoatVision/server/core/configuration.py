#! /usr/bin/env python

#    Copyright (C) 2012-2014  Octets - octets.etsmtl.ca
#
#    This file is part of SeaGoatVision.
#
#    SeaGoatVision is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Description : Configuration manage configuration file.
"""
# Note, this file should not import core object, because they depend of him

import os
import json
from SeaGoatVision.commons import log

logger = log.get_logger(__name__)


class Configuration(object):
    _instance = None

    def __new__(cls):
        # Singleton
        if not cls._instance:
            from configurations.public import config as public_config

            try:
                from configurations.private import config as private_config
            except BaseException as e:
                logger.info(
                    "Ignore missing private configuration because: %s" % e)
            # first instance
            cls.public_config = public_config
            try:
                if private_config.active_configuration:
                    cls.private_config = private_config
                else:
                    cls.private_config = None
            except BaseException:
                cls.private_config = None
            cls.print_configuration = False
            cls.verbose = False
            # instance class
            cls._instance = super(Configuration, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.verbose = False
        path = "configurations/"
        if self.get_is_show_public_filterchain():
            self.dir_filterchain = path + "public/filterchain/"
            self.dir_media = path + "public/"
            if not self.print_configuration:
                logger.info("Loading public configuration.")
        else:
            self.dir_filterchain = path + "private/filterchain/"
            self.dir_media = path + "private/"
            if not self.print_configuration:
                logger.info("Loading private configuration.")
        self.print_configuration = True
        self.type_filterchain = "filterchain"
        self.type_media = "media"
        self.ext_filterchain = ".%s" % self.type_filterchain
        self.ext_media = ".%s" % self.type_media

    # Setter ####
    def set_verbose(self, is_verbose):
        self.verbose = is_verbose

    # General config
    def _get_conf(self, var_name, default_value):
        if self.private_config:
            return getattr(self.private_config, var_name, default_value)
        return default_value

    def get_verbose(self):
        if self.verbose:
            return True

        return self._get_conf("verbose",
                              self.public_config.verbose)

    def get_tcp_output_config(self):
        return self._get_conf("port_tcp_output",
                              self.public_config.port_tcp_output)

    def get_lst_media_config(self):
        return self._get_conf("lst_media",
                              self.public_config.lst_media)

    def get_is_show_public_filterchain(self):
        return self._get_conf("show_public_filterchain",
                              self.public_config.show_public_filterchain)

    def get_is_show_public_filter(self):
        return self._get_conf("show_public_filter",
                              self.public_config.show_public_filter)

    def get_is_show_private_filter(self):
        return self._get_conf("active_configuration",
                              self.public_config.active_configuration)

    def get_path_save_record(self):
        return self._get_conf("path_save_record",
                              self.public_config.path_save_record)

    def get_log_file_path(self):
        return self._get_conf("log_path",
                              self.public_config.log_path)

    def get_dct_cmd_on_start(self):
        return self._get_conf("cmd_on_start",
                              self.public_config.cmd_on_start)

    # Filterchain
    def list_filterchain(self):
        if not os.path.isdir(self.dir_filterchain):
            return []
        return [files[:-len(self.ext_filterchain)] for files in
                os.listdir(self.dir_filterchain) if
                files.endswith(self.ext_filterchain)]

    def read_filterchain(self, filterchain_name):
        file_name = self._get_fc_filename(filterchain_name)
        return self._read_configuration(file_name, self.type_filterchain,
                                        False)

    def read_media(self, media_name):
        file_name = self._get_media_filename(media_name)
        return self._read_configuration(file_name, self.type_media, True)

    def _read_configuration(self, file_name, type_name, ignore_not_exist):
        if not self._is_config_exist(file_name, type_name, ignore_not_exist):
            return None
        f = open(file_name, "r")
        if not f:
            log.print_function(
                logger.error, "Can't open %s %s." % (file_name, type_name))
            return None
        str_value = f.readlines()
        try:
            value = json.loads("".join(str_value))
        except BaseException:
            log.print_function(
                logger.error, "The file %s not contain json data." % file_name)
            value = None
        f.close()
        return value

    def write_filterchain(self, filterchain):
        return self._write_configuration(filterchain, self._get_fc_filename)

    def write_media(self, media):
        return self._write_configuration(media, self._get_media_filename)

    @staticmethod
    def _write_configuration(obj, fct_filename):
        file_name = fct_filename(obj.get_name())
        f = open(file_name, "w")
        if not f:
            return False
        str_value = json.dumps(obj.serialize(is_config=True), indent=4)
        f.write(str_value)
        f.close()
        return True

    def delete_filterchain(self, filterchain_name):
        file_name = self._get_fc_filename(filterchain_name)
        try:
            os.remove(file_name)
        except OSError:
            return False
        return True

    @staticmethod
    def _is_config_exist(file_name, type_name, ignore_not_exist):
        if not os.path.isfile(file_name):
            if not ignore_not_exist:
                log.print_function(logger.error, "The %s config %s\
                                    not exist." % (file_name, type_name))
            return False
        return True

    def is_filterchain_exist(self, filterchain_name):
        file_name = self._get_fc_filename(filterchain_name)
        return self._is_config_exist(file_name, self.type_filterchain, True)

    def is_media_exist(self, media_name):
        file_name = self._get_media_filename(media_name)
        return self._is_config_exist(file_name, self.type_media, True)

    def _get_fc_filename(self, filterchain_name):
        return "%s%s%s" % (self.dir_filterchain,
                           filterchain_name,
                           self.ext_filterchain)

    def _get_media_filename(self, media_name):
        return "%s%s%s" % (self.dir_media, media_name, self.ext_media)
