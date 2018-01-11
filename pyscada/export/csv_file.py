from __future__ import unicode_literals
import csv
import os
import logging

logger = logging.getLogger(__name__)


def unix_time_stamp_to_excel_datenum(timestamp):
    """
    convert from unix time (seconds since 01/01/1970) to Excel datenum (days since 01/01/1900)
    """
    return (timestamp / 86400.0) + 25569.0


class ExcelCompatibleCSV:
    def __init__(self, filename, **kwargs):
        self.filename = os.path.expanduser(filename)
        self.data = {}
        self.header = {}
        self.data_rows = 0
        self.header_is_writen = False
        self.dialect = 'excel'  # default is excel

    def write_data(self, name, data, **kwargs):
        if name in self.data:
            # append data
            self.data[name] += data
            self.data_rows = max(self.data_rows, len(self.data[name]))
        else:
            # new entry
            self.data[name] = data
            self.data_rows = max(self.data_rows, len(self.data[name]))  # update len
            self.header[name] = kwargs.copy()

    def write_file(self):
        # check the data
        # data has to have the same len
        del_keys = []
        for key in self.data:
            if len(self.data[key]) != self.data_rows:
                del_keys.append(key)
        for i in del_keys:
            self.data.pop(i, None)
            self.header.pop(i, None)
        # construct the write arrays
        keys = self.data.keys()
        output = zip(*self.data.values())
        # truncate file on first write, otherwise append
        write_mode = 'a' if self.header_is_writen else 'w'
        with open(self.filename, write_mode) as f:
            writer = csv.writer(f, dialect=self.dialect)
            if not self.header_is_writen:
                writer.writerow(keys)
                self.header_is_writen = True
            writer.writerows(output)
        # reset internal data
        self.data = {}
        self.data_rows = 0
        self.header = {}

    def reopen(self):
        self.write_file()

    def close_file(self):
        self.write_file()
