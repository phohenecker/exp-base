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


import abc
import os
import typing

import insanity
import streamtologger

import expbase
import expbase.base_config as base_config


__author__ = "Patrick Hohenecker"
__copyright__ = "Copyright (c) 2020, Patrick Hohenecker"
__license__ = "BSD-2-Clause"
__version__ = "0.1.0-rc.1"
__date__ = "22 Jul 2020"
__maintainer__ = "Patrick Hohenecker"
__email__ = "patrick.hohenecker@gmx.at"
__status__ = "Development"


class EvaluationExecutor(metaclass=abc.ABCMeta):
    """An abstract base class that has to be extended with the code that implements the evaluation procedure.

    This class defines only one public method, :meth:`run`, which first sets up the logging facilities, and then
    launches the evaluation.

    Actual implementations are required to define the abstract method :meth:`_run_evaluation`, which is supposed to
    implement the evaluation procedure. In addition to this, subclasses may override :meth:`_init` in order to implement
    initialization code that would usually be put into :meth:`__init__`. The reason for this is that instances of
    ``EvaluationExecutor`` might be moved between processes, and :meth:`_init` is guaranteed to be executed right before
    and in the same process as :meth:`_run_evaluation`.

    Attributes:
        _ckpt (str): The (private) specification of the checkpoint to evaluate. This has been passed to the constructor
            of the instance of ``EvaluationExecutor``.
        _conf: The (private) configuration that has been provided to the constructor of the instance of
            ``EvaluationExecutor``. This is a subclass of :class:`base_class.BaseClass`.
    """

    def __init__(self, conf: base_config.BaseConfig, ckpt: typing.Optional[str]):
        """Creates a new instance of ``EvaluationExecutor``.

        Args:
            conf (:class:`base_config.BaseConfig`): The configuration of the conducted experiment.
            ckpt (str): The checkpoint to evaluate. This arg identifies a checkpoint that was just created by a training
                process, and is supposed to be evaluated (in parallel to the training) now. Notice that this is
                ``None``, if ``conf.test`` has been set to ``True`` (cf. :attr:`base_config.BaseConfig.test`), which
                means that a model is just being tested without any further training.
        """

        # sanitize args
        insanity.sanitize_type("conf", conf, base_config.BaseConfig)
        insanity.sanitize_type("ckpt", ckpt, str, none_allowed=True)

        # store args
        self._ckpt = ckpt
        self._conf = conf

    #  METHODS  ########################################################################################################

    def _init(self) -> None:
        """Initialization routines.

        This method does not implement any functionality by default, but is supposed to be overridden with code that
        would be put in ``__init__`` otherwise. The public method :meth:`run` invokes ``_init`` right before it invokes
        :meth:`_run_evaluation`.
        """

        pass  # nothing to do -> this method is simply a stub that may be overridden

    @abc.abstractmethod
    def _run_evaluation(self) -> None:
        """This method implements the actual evaluation procedure."""

    def run(self) -> None:
        """Starts the evaluation.

        This method first runs all of the necessary preparatory actions, and then launches the actual evaluation.
        """

        # redirect entire output to a log file
        streamtologger.redirect(
                target=os.path.join(self._conf.results_dir, self._conf.evaluation_log),
                print_to_screen=False,
                append=True,
                header_format=expbase.LOG_LINE_HEADER
        )

        # initialize this training executor
        self._init()

        # start evaluation
        self._run_evaluation()
