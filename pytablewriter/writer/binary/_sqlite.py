# encoding: utf-8

from __future__ import absolute_import, unicode_literals

from os.path import abspath

import tabledata

from ._interface import AbstractBinaryTableWriter


class SqliteTableWriter(AbstractBinaryTableWriter):
    """
    A table writer class for SQLite database.

    .. py:method:: write_table()

        Write a table to a SQLite database.

        :raises pytablewriter.EmptyTableNameError:
            If the |table_name| is empty.
        :raises pytablewriter.EmptyHeaderError:
            If the |headers| is empty.
        :raises pytablewriter.EmptyValueError:
            If the |value_matrix| is empty.
        :Example:
            :ref:`example-sqlite-table-writer`
    """

    FORMAT_NAME = "sqlite"

    @property
    def format_name(self):
        return self.FORMAT_NAME

    @property
    def support_split_write(self):
        return True

    def __init__(self):
        import copy
        import dataproperty

        super(SqliteTableWriter, self).__init__()

        self.is_padding = False
        self.is_formatting_float = False
        self._use_default_header = True

        self._is_require_table_name = True
        self._is_require_header = True

        self._quoting_flags = copy.deepcopy(dataproperty.NOT_QUOTING_FLAGS)

    def __del__(self):
        self.close()

    def is_opened(self):
        return self.stream is not None

    def open(self, file_path):
        """
        Open a SQLite database file.

        :param str file_path: SQLite database file path to open.
        """

        from simplesqlite import SimpleSQLite

        if self.is_opened():
            if self.stream.database_path == abspath(file_path):
                self._logger.logger.debug(
                    "database already opened: {}".format(self.stream.database_path)
                )
                return

            self.close()

        self._stream = SimpleSQLite(file_path, "w")

    def dump(self, output, close_after_write=True):
        """Write data to the SQLite database file.

        Args:
            output (file descriptor or filepath):
            close_after_write (bool, optional):
                Close the output after write.
                Defaults to |True|.
        """

        self.open(output)
        try:
            self.write_table()
        finally:
            if close_after_write:
                self.close()

    def _write_table(self):
        self._verify_value_matrix()
        self._preprocess()

        table_data = tabledata.TableData(
            self.table_name,
            self.headers,
            [
                [value_dp.data for value_dp in value_dp_list]
                for value_dp_list in self._table_value_dp_matrix
            ],
        )
        self.stream.create_table_from_tabledata(table_data)

    def _write_value_row_separator(self):
        pass
