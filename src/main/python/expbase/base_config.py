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


import os
import random
import typing

import argmagiq
import insanity


__author__ = "Patrick Hohenecker"
__copyright__ = "Copyright (c) 2020, Patrick Hohenecker"
__license__ = "BSD-2-Clause"
__version__ = "0.1.0-rc.1"
__date__ = "22 Jul 2020"
__maintainer__ = "Patrick Hohenecker"
__email__ = "patrick.hohenecker@gmx.at"
__status__ = "Development"


class BaseConfig(object):
    """This class defines a few basic configurations, and has to be extended by any custom configuration class that is
    provided to an instance of :class:`expbase.experiment.Experiment`.
    """

    DEFAULT_EVALUATION_LOG = "eval.log"
    DEFAULT_GENERAL_LOG = "experiment.log"
    DEFAULT_QUIET = False
    DEFAULT_RESULTS_DIR = os.path.join(".", "results")
    DEFAULT_TEST = False
    DEFAULT_TRAINING_LOG = "train.log"

    #  CONSTRUCTOR  ####################################################################################################

    def __init__(self):

        self._ckpt = None
        self._evaluation_log = self.DEFAULT_EVALUATION_LOG
        self._general_log = self.DEFAULT_GENERAL_LOG
        self._quiet = self.DEFAULT_QUIET
        self._results_dir = self.DEFAULT_RESULTS_DIR
        self._seed = random.randrange(100000)
        self._test = self.DEFAULT_TEST
        self._title = None
        self._training_log = self.DEFAULT_TRAINING_LOG

    #  PROPERTIES  #####################################################################################################

    @argmagiq.optional
    @property
    def ckpt(self) -> typing.Optional[str]:
        """str: The path of a checkpoint to start from."""

        return self._ckpt

    @ckpt.setter
    def ckpt(self, ckpt: str) -> None:

        ckpt = str(ckpt)
        if not os.path.isfile(ckpt):
            raise ValueError(f"<ckpt> does not refer to an existing file: '{ckpt}'")
        self._ckpt = ckpt

    @property
    def evaluation_log(self) -> str:
        """str: The name of the log file for the evaluation process that is created in the results directory."""

        return self._evaluation_log

    @evaluation_log.setter
    def evaluation_log(self, evaluation_log: str) -> None:

        evaluation_log = str(evaluation_log)
        if len(evaluation_log) == 0:
            raise ValueError("<evaluation_log> must not be the empty string")
        self._evaluation_log = evaluation_log

    @property
    def general_log(self) -> str:
        """str: The name of the default log file that is created in the results directory."""

        return self._general_log

    @general_log.setter
    def general_log(self, general_log: str) -> None:

        general_log = str(general_log)
        if len(general_log) == 0:
            raise ValueError("<general_log> must not be the empty string")
        self._general_log = general_log

    @property
    def quiet(self) -> bool:
        """bool: Specifies whether the application should be quiet, i.e., not print any output to the screen."""

        return self._quiet

    @quiet.setter
    def quiet(self, quiet: bool) -> None:
        self._quiet = bool(quiet)

    @property
    def results_dir(self) -> str:
        """str: The path of the directory that results should be stored in."""

        return self._results_dir

    @results_dir.setter
    def results_dir(self, results_dir: str) -> None:

        results_dir = str(results_dir)
        if not results_dir:
            raise ValueError("<results_dir> must not be the empty string")
        self._results_dir = results_dir

    @argmagiq.optional
    @property
    def seed(self) -> typing.Optional[int]:
        """int: The seed to use for initializing RNGs."""

        return self._seed

    @seed.setter
    def seed(self, seed: int) -> None:

        insanity.sanitize_type("seed", seed, int)
        self._seed = seed

    @property
    def test(self) -> bool:
        """bool: If specified, then a test is run instead of any training."""

        return self._test

    @test.setter
    def test(self, test: bool) -> None:
        self._test = bool(test)

    @argmagiq.optional
    @property
    def title(self) -> typing.Optional[str]:
        """str: A title for the conducted experiment."""

        return self._title

    @title.setter
    def title(self, title: str) -> None:

        title = str(title)
        if not title:
            raise ValueError("<title> must not be the empty string")
        self._title = title

    @property
    def training_log(self) -> str:
        """str: The name of the log file for the training process that is created in the results directory."""

        return self._training_log

    @training_log.setter
    def training_log(self, training_log: str) -> None:

        training_log = str(training_log)
        if len(training_log) == 0:
            raise ValueError("<training_log> must not be the empty string")
        self._training_log = training_log
