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


"""Helper functions for printing section headers and endings."""


__author__ = "Patrick Hohenecker"
__copyright__ = "Copyright (c) 2020, Patrick Hohenecker"
__license__ = "BSD-2-Clause"
__version__ = "0.1.0-rc.1"
__date__ = "22 Jul 2020"
__maintainer__ = "Patrick Hohenecker"
__email__ = "patrick.hohenecker@gmx.at"
__status__ = "Development"


def print_end(title: str, level: int = 0, width: int = 160) -> None:
    """Prints an end of a section.

    This function is the counterpart of the function :func:`print_header`.

    Args:
        title (str): The title of the section that the end is printed for. Notice that ``"End of"`` is prepended to the
            provided ``title``.
        level (int): Specifies the level of the section that is ended. Notice that this function distinguishes the
            levels 0 (highest), 1, and everything else (lowest level) only.
        width (int, optional): The width of the end to print.
    """

    if level == 0:
        title_pattern = "{:#>%d} ########" % (width - 9)
        print(title_pattern.format(" END OF " + str(title).upper()))
    elif level == 1:
        title_pattern = "{:/>%d} ////////" % (width - 9)
        print(title_pattern.format(" END OF " + str(title).upper()))
    else:
        title_pattern = "{:->%d} --------" % (width - 9)
        print(title_pattern.format(" END OF " + str(title).upper()))

    # add final blank line
    print()


def print_header(title: str, level: int = 0, width: int = 160) -> None:
    """Prints a header for the section with the provided title.

    This function is the counterpart of the function :func:`print_end`.

    Args:
        title (str): The title to print.
        level (int): Specifies the level of the section that the header is printed for. Notice that this function
            distinguishes the levels 0 (highest), 1, and everything else (lowest level) only.
        width (int, optional): The width of the header to print.
    """

    if level == 0:
        title_pattern = "#  {:%d}  #" % (width - 6)
        print("#" * width)
        print(title_pattern.format(str(title).upper()))
        print("#" * width)
    elif level == 1:
        title_pattern = "//////// {:/<%d}" % (width - 9)
        print(title_pattern.format(str(title).upper() + " "))
    else:
        title_pattern = "-------- {:-<%d}" % (width - 9)
        print(title_pattern.format(str(title).upper() + " "))

    # add final blank line
    print()
