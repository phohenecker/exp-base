# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                                     #
#   BSD 2-Clause License                                                              #
#                                                                                     #
#   Copyright (c) 2020, Patrick Hohenecker                                            #
#   All rights reserved.                                                              #
#                                                                                     #
#   Redistribution and use in source and binary forms, with or without                #
#   modification, are permitted provided that the following conditions are met:       #
#                                                                                     #
#   1. Redistributions of source code must retain the above copyright notice, this    #
#      list of conditions and the following disclaimer.                               #
#                                                                                     #
#   2. Redistributions in binary form must reproduce the above copyright notice,      #
#      this list of conditions and the following disclaimer in the documentation      #
#      and/or other materials provided with the distribution.                         #
#                                                                                     #
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"       #
#   AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE         #
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE    #
#   DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE      #
#   FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL        #
#   DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR        #
#   SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER        #
#   CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,     #
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE     #
#   OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.              #
#                                                                                     #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


import collections
import typing

import insanity


__author__ = "Patrick Hohenecker"
__copyright__ = "Copyright (c) 2020, Patrick Hohenecker"
__license__ = "BSD-2-Clause"
__version__ = "0.1.0-rc.1"
__date__ = "22 Jul 2020"
__maintainer__ = "Patrick Hohenecker"
__email__ = "patrick.hohenecker@gmx.at"
__status__ = "Development"


def _center_just(text: str, width: int):
    """Pads the provided string left and right such that it has a specified width and is centered.

    Args:
        text (str): The string to pad.
        width (int): The desired width of the padded ``text``.

    Returns:
        str: The padded ``text``.
    """

    len_diff = width - len(text)
    if len_diff <= 0:
        return text

    pad_before = len_diff // 2
    pad_after = len_diff - pad_before

    return (" " * pad_before) + text + (" " * pad_after)


# ==================================================================================================================== #
#  CLASS TABLE                                                                                                         #
# ==================================================================================================================== #


class Table(object):
    """A table that can be printed to the command line."""

    def __init__(self, title: str = None, column_sep: str = "|", padding: int = 1):
        """Creates a new ``Table`` with the provided title.

        Args:
            title (str, optional): The title of the newly created ``Table``.
            column_sep (str, optional): The character(s) used for "drawing" lines between columns.
            padding (int, optional): The padding to use in table cells.
        """

        insanity.sanitize_type("padding", padding, int)
        insanity.sanitize_range("padding", padding, minimum=0)

        self._column_sep = str(column_sep)
        self._data = []
        self._padding = padding
        self._title = None if title is None else str(title)
        self._width = None

    #  MAGIC FUNCTIONS  ################################################################################################

    def __str__(self) -> str:

        self._pack()

        sep = "+{}+".format("=" * (self._width - 2 * len(self._column_sep)))  # -> a horizontal line
        str_table = sep + "\n"  # -> stores the string representation of the table

        # add the title to the output, if it exists
        if self._title is not None:  # -> there is a title that has to be added

            str_table += "{0}{1}{0}\n".format(
                    self._column_sep,
                    _center_just(self._title, self._width - 2 * len(self._column_sep))
            )
            str_table += sep + "\n"

        # add all sections to the output
        for index, sec in enumerate(self._data):  # -> iterate over all sections

            str_table += str(sec)
            str_table += sep
            if index < len(self._data) - 1:
                str_table += "\n"

        return str_table

    #  METHODS  ########################################################################################################

    def _pack(self) -> None:
        """Computes the layout of the ``Table``."""

        # get column widths for all sections
        col_widths = [sec.column_widths for sec in self._data]

        # check if the table is uniform, i.e., all sections have equal number of columns
        uniform = len(set(len(x) for x in col_widths)) == 1

        if uniform:  # -> all sections contain an equal number of columns

            # -> in this case, we use equal column widths across all sections

            # compute the column widths
            final_col_widths = [0] * len(col_widths[0])
            for sec_widths in col_widths:
                for index, width in enumerate(sec_widths):
                    final_col_widths[index] = max(final_col_widths[index], width)

            # set (the equal) column width in all sections
            for sec in self._data:
                sec.column_widths = final_col_widths

            # store the width of the entire table
            self._width = self._data[0].width

        else:  # -> sections contain different numbers of columns

            # determine the width of the entire table -> this is the max of all section widths
            self._width = max([sec.width for sec in self._data])

            # specify the width of every section to match the width of the table
            for sec in self._data:
                sec.width = self._width

        # check if there is enough space for the title + increase the size, if necessary
        if self._title is not None:

            min_width = len(self._title) + 2 * (self._padding + len(self._column_sep))

            if self._width < min_width:  # -> the width has to be increased
                for sec in self._data:
                    sec.width = min_width
                self._width = min_width

    def add(
            self,
            data: typing.Sequence[typing.Sequence[str]],
            section_title: str = None,
            column_labels: typing.Sequence[str] = None
    ) -> "Table":
        """Adds a section to the ``Table``.

        Args:
            data (Sequence[Sequence[str]]): The data displayed in the created section provided row by row. Notice that
                all rows in ``data`` need to have the same length.
            section_title (str, optional): An optional title of the newly created section.
            column_labels (Sequence[str], optional): Labels to display for the columns in the new section.
        """

        # sanitize args
        insanity.sanitize_type("data", data, collections.Sequence)
        insanity.sanitize_iterable("data", data, min_length=1, error_msg="Cannot add an empty section!")
        for i in range(1, len(data)):
            if len(data[i]) != len(data[0]):
                raise ValueError("All rows need to be of equal length!")
        insanity.sanitize_iterable("data", data, elements_type=collections.Sequence)
        insanity.sanitize_iterable("column_labels", column_labels, target_length=len(data[0]), none_allowed=True)

        # create an according section object
        self._data.append(
                _Section(
                        data,
                        title=section_title,
                        column_labels=column_labels,
                        column_sep=self._column_sep,
                        padding=self._padding
                )
        )

        return self

    @staticmethod
    def create_table(data: dict, title: str = None) -> "Table":
        """Creates a ``Table`` based on the provided ``dict``.

        Args:
            data (dict): The data to create the ``Table`` for.
            title (str, optional): An optional title of the newly created ``Table``.

        Returns:
            Table: The constructed ``Table``.
        """

        tab = Table(title=title)
        tab.add(list(data.items()))

        return tab


# ==================================================================================================================== #
#  CLASS _SECTION                                                                                                      #
# ==================================================================================================================== #


class _Section(object):
    """Represents one section of a table."""

    def __init__(
            self,
            data: typing.Sequence[typing.Sequence[str]],
            title: str = None,
            column_labels: typing.Sequence[str] = None,
            column_sep: str = "|",
            padding: int = 1
    ):
        """Creates a new instance of ``_Section``.

        Args:
            data (Collection[Collection[str]]): The data that is contained in the newly created ``_Section``.
            title (str, optional): An optional title of the newly created ``_Section``.
            column_labels (Sequence[str], optional): Labels to display for the columns in the new section.
            column_sep (str, optional): The character(s) used for "drawing" lines between columns.
            padding (int, optional): The padding to use in table cells.
        """

        # define attributes
        self._column_sep = str(column_sep)
        self._data = None
        self._has_labels = column_labels is not None
        self._num_rows = len(data) + int(column_labels is not None)
        self._padding = padding
        self._title = None if title is None else str(title)

        # group data by column
        if column_labels is not None:
            col_data = [[x] for x in column_labels]
        else:
            col_data = [[] for _ in range(len(data[0]))]
        for row in data:
            for index, value in enumerate(row):
                col_data[index].append(value)

        # create columns
        self._data = [_Column(x, padding=self._padding) for x in col_data]

        # expand columns if necessary
        if self._title is not None:
            min_width = len(self._title) + 2 * self._padding
            if self.width < min_width:
                self.width = min_width

    #  MAGIC FUNCTIONS  ################################################################################################

    def __len__(self) -> int:

        return len(self._data)

    def __str__(self) -> str:

        # prepare horizontal separator
        sep = "+"
        for col in self._data:
            sep += "-" * col.width + "+"
        sep += "\n"

        # create title
        str_section = ""
        if self._title is not None:
            str_section += self._column_sep
            str_section += _center_just(self._title, self.width - 2 * len(self._column_sep))
            str_section += self._column_sep
            str_section += "\n"
            str_section += sep

        # create section content
        for row in range(self._num_rows):

            # add column data to current row
            for col in self._data:
                str_section += self._column_sep + col[row]
            str_section += self._column_sep + "\n"

            # if the current row contains column labels -> add separator
            if row == 0 and self._has_labels:
                str_section += sep

        return str_section

    #  PROPERTIES  #####################################################################################################

    @property
    def column_widths(self) -> typing.Tuple[int, ...]:
        """tuple[int]: The widths of the columns in the ``_Section``."""

        return tuple(x.width for x in self._data)

    @column_widths.setter
    def column_widths(self, column_widths: typing.Iterable[int]) -> None:

        for index, width in enumerate(column_widths):
            self._data[index].width = width

    @property
    def width(self) -> int:
        """int: The total width of the ``_Section``."""

        return sum(self.column_widths) + (len(self) + 1) * len(self._column_sep)

    @width.setter
    def width(self, width: int) -> None:

        # remove width that is occupied by the column separators
        remaining_width = width - (len(self) + 1) * len(self._column_sep)

        # if the specified width is smaller than the current one, then reset all columns to their minimum width
        reset_all = width < self.width

        # compute remaining width and possible reset columns
        for x in self._data:
            if reset_all:
                x.reset()
            remaining_width -= x.width

        # check if there is enough width for all columns at all
        if remaining_width < 0:
            raise ValueError("The <width> {} is too narrow to cover all columns".format(width))

        # add additional space to columns
        num_columns = len(self)
        for i in range(remaining_width):
            current_col = - (i % num_columns) - 1  # since we go from left to right
            self._data[current_col].width += 1


# ==================================================================================================================== #
#  CLASS _COLUMN                                                                                                       #
# ==================================================================================================================== #


class _Column(object):
    """Represents one column of a section of a table."""

    def __init__(self, data: typing.Sequence[str], padding: int = 1):
        """Creates a new instance of ``_Column``.

        Args:
            data (Sequence[str]): The data that is contained in the newly created ``_Column``.
            padding (int, optional): The padding that should be used in the created ``_Column``.
        """

        # define attributes
        self._data = data
        self._min_width = None
        self._padding = padding
        self._width = None

        # set column width to minimum
        self._min_width = self._compute_min_width()
        self._width = self._min_width

    #  MAGIC FUNCTIONS  ################################################################################################

    def __getitem__(self, item: int) -> str:

        return (" " * self._padding) + str(self._data[item]).ljust(self._width - self._padding)

    #  PROPERTIES  #####################################################################################################

    @property
    def width(self) -> int:
        """int: The width of the ``_Column``."""

        return self._width

    @width.setter
    def width(self, width: int) -> None:

        insanity.sanitize_range("width", width, minimum=self._min_width)
        self._width = width

    #  METHODS  ########################################################################################################

    def _compute_min_width(self) -> int:
        """Computes the minimum width of the ``_Column`` based on its content and padding.

        Returns:
            int: The computed width.
        """

        return max([len(str(x)) for x in self._data]) + 2 * self._padding

    def reset(self) -> None:
        """Rests a ``_Column`` to its minimum width."""

        self._width = self._min_width
