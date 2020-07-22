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


import time

import insanity


__author__ = "Patrick Hohenecker"
__copyright__ = "Copyright (c) 2020, Patrick Hohenecker"
__license__ = "BSD-2-Clause"
__version__ = "0.1.0-rc.1"
__date__ = "22 Jul 2020"
__maintainer__ = "Patrick Hohenecker"
__email__ = "patrick.hohenecker@gmx.at"
__status__ = "Development"


class Timer(object):
    """A convenience class for measuring and printing timings.

    Often times, we are interested in the execution times of certain portions of our code, and want these to be printed
    to the command line. This class allows for achieving this by means of a ``with`` block as follows:

        with Timer("finished setup"):
            # this is the code whose execution time is measured
            ...

    In this particular example, the message "finished setup in 1.234s" would be printed to the screen at the end of
    the ``with`` block.
    """

    def __init__(self, message: str, decimal_places: int = 3, terminal_break: bool = False, skip_output: bool = False):
        """Creates a new instance of ``Timer``.

        Args:
            message (str): The message to print at the end of the ``with`` block. Notice that the measured time, as
                string ``" in X.XXXs"``, is appended to the provided message automatically.
                this message
            decimal_places (int, optional): The number of decimal places to print for the time, which is measured and
                printed in seconds.
            terminal_break (bool, optional): Indicates whether to add an additional line break to the printed message.
            skip_output (bool, optional): If ``True``, then no output is printed to the screen.
        """

        # sanitize args
        insanity.sanitize_type("decimal_places", decimal_places, int)
        insanity.sanitize_range("decimal_places", decimal_places, minimum=0)

        # create the message to print at the end of the with-block
        self._message = str(message).strip() + " in {:.%df}s" % decimal_places
        if terminal_break:
            self._message += "\n"

        self._start = None  # the time when the clock is started
        self._total = 0  # the total time measured

        self._skip_output = bool(skip_output)  # indicates whether to print the time at the end of a ``with`` block

    #  MAGIC FUNCTIONS  ################################################################################################

    def __enter__(self):

        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        self.stop()
        if not self._skip_output:
            print(self._message.format(self._total))

    #  PROPERTIES  #####################################################################################################

    @property
    def total(self) -> float:
        """float: The total time that has been measured by the ``Timer``.

        Notice that this attribute is updated at the end of a ``with``-block or whenever :meth:`Timer.stop` is invoked
        manually.
        """

        return self._total

    #  METHODS  ########################################################################################################

    def skip_output(self) -> None:
        """Instructs the ``Timer`` to not print the time at the end of a ``with`` block."""

        self._skip_output = True

    def start(self) -> None:
        """Starts the clock.

        This method is invoked automatically at the beginning of a ``with``-block``, but it may as well be called
        manually in order to restart a `Timer` that has been stopped before. Note that nothing happens if the `Timer`
        is running already.
        """

        if self._start is None:
            self._start = time.time()

    def stop(self) -> None:
        """Stops the clock.

        This method may be called manually in order to stop the clock before the actual end of a ``with`` block is
        reached. Note that nothing happens if the ``Timer`` is stopped already.
        """

        if self._start is not None:
            self._total += time.time() - self._start
            self._start = None
