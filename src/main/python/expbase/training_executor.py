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
import multiprocessing.queues as queues
import os

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


class TrainingExecutor(metaclass=abc.ABCMeta):
    """An abstract base class that has to be extended with code that implements the training procedure.

    This class defines only one public method, :meth:`run`, which first sets up the logging facilities and then
    launches the training.

    Actual implementations are required to define the abstract method :meth:`_run_training`, which is supposed to
    implement the training procedure. In addition to this, subclasses may override :meth:`_init` in order to implement
    initialization code that would usually be put into :meth:`__init__`. The reason for this is that instances of
    ``TrainingExecutor`` might be moved between processes, and :meth:`_init` is guaranteed to be executed right before
    and in the same process as :meth:`_run_training`.

    Any experiment, implemented by means of the package :mod:`expbase`, relies on the training process to notify the
    controller of the experiment about any checkpoints that have been created. To that end, :meth:`_run_training` is
    supposed to make use of :meth:`_deliver_ckpt` in order to send strings identifying created checkpoints to the
    controller. Whenever the controller receives such a string, it creates a new instance of
    :class:`expbase.evaluation_executor.EvaluationExecutor`, and launches the evaluation of the referenced checkpoint
    in parallel in a new process. Notice that the format of the exchanged string does not have to follow any specific
    rules, but implementations need to ensure that the code for evaluation is able to find the specified checkpoint.

    Attributes:
        _conf: The (private) configuration that has been provided to the constructor of the instance of
            ``TrainingExecutor``. This is a subclass of :class:`base_class.BaseClass`.
    """

    def __init__(self, conf: base_config.BaseConfig, ckpt_queue: queues.Queue):
        """Creates a new instance of ``TrainingExecutor``.

        Args:
            conf (:class:`base_config.BaseConfig`): The configuration of the conducted experiment.
            ckpt_queue (queues.Queue): The queue that is used for sending created checkpoints to the controller of the
                experiment.
        """

        # sanitize args
        insanity.sanitize_type("conf", conf, base_config.BaseConfig)
        insanity.sanitize_type("ckpt_queue", ckpt_queue, queues.Queue)

        # store args
        self._ckpt_queue = ckpt_queue
        self._conf = conf

    #  METHODS  ########################################################################################################

    def _deliver_ckpt(self, ckpt: str) -> None:
        """Notifies the controller of the experiment, which launched the ``TrainingExecutor`,` about a checkpoint that
        has been created.

        Args:
            ckpt (str): An (application-specific) description of the created checkpoint that allows for finding and
                evaluating it.
        """

        self._ckpt_queue.put(ckpt)

    def _init(self) -> None:
        """Initialization routines.

        This method does not implement any functionality by default, but is supposed to be overridden with code that
        would be put in ``__init__`` otherwise. The public method :meth:`run` invokes ``_init`` right before it invokes
        :meth:`_run_training`.
        """

        pass  # nothing to do -> this method is simply a stub that may be overridden

    @abc.abstractmethod
    def _run_training(self) -> None:
        """This method implements the actual training procedure."""

    def run(self) -> None:
        """Starts the training.

        This method first runs all of the necessary preparatory actions, and then launches the actual experiment.
        """

        # redirect entire output to a log file
        streamtologger.redirect(
                target=os.path.join(self._conf.results_dir, self._conf.training_log),
                print_to_screen=False,
                append=False,
                header_format=expbase.LOG_LINE_HEADER
        )

        # initialize this training executor
        self._init()

        # start training
        self._run_training()
