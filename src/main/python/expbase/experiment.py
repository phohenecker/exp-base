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


import datetime
import json
import multiprocessing as mp
import multiprocessing.context as context
import multiprocessing.process as process
import os
import queue
import sys
import typing

import argmagiq
import insanity
import streamtologger

import expbase
import expbase.base_config as base_config
import expbase.evaluation_executor as evaluation_executor
import expbase.training_executor as training_executor
import expbase.util.table as table


__author__ = "Patrick Hohenecker"
__copyright__ = "Copyright (c) 2020, Patrick Hohenecker"
__license__ = "BSD-2-Clause"
__version__ = "0.1.0-rc.1"
__date__ = "22 Jul 2020"
__maintainer__ = "Patrick Hohenecker"
__email__ = "patrick.hohenecker@gmx.at"
__status__ = "Development"


class Experiment(object):
    """A controller class that implements the high-level control flow of a conducted experiment.

    An experiment is supposed to be started by invoking :meth:`run`. This, in turn, executes the following steps:
    1. parse command-line args, and create a config object,
    2. perform additional sanity checks for the created config (:meth:`_sanitize_config`),
    3. prepare the results directory (:meth:`_prepare_results_dir`),
    4. store the used config as JSON file in the results directory (:meth:`_store_config`),
    5. set up logging,
    6. print the provided config (:meth:`_print_config`),
    7. launch the training procedure in a separate process, and
    8. wait for checkpoints to be created and launch the evaluation of each in a separate process as it is created.
    Steps 2, 3, 4, and 6 may be adjusted by overriding the referenced methods. The program logic for training and
    evaluation that is used in steps 6 and 7, however, has to be implemented in two separate classes, subclassing
    :class:`training_executor.TrainingExecutor` and :class:`evaluation_executor.EvaluationExecutor`, respectively, each
    of which has to be provided to :meth:`__init__`.
    """

    CHECK_ALIVE_INTERVAL = 10
    """int: The interval for checking whether the training process is still alive in seconds."""

    PROCESS_START_METHOD = "spawn"
    """str: The method that is used for creating child processes."""

    #  CONSTRUCTOR  ####################################################################################################

    def __init__(
            self,
            training_class: type,
            evaluation_class: type,
            config_class: type,
            app_name: str,
            app_description: str,
            parallel_eval: bool = False
    ):
        """Creates a new instance of ``Experiment``.

        Args:
            training_class (type): The class that implements the training procedure. This has to be a subclass of
                :class:`training_executor.TrainingExecutor`.
            evaluation_class (type): The class that implements the evaluation procedure. This has to be a subclass of
                :class:`evaluation_executor.EvaluationExecutor`.
            config_class (type): The configuration class that is used for parsing command-line args.
            app_name (str): The name that is printed for this application in its synopsis.
            app_description (str): The description that is printed in the help text for this application.
            parallel_eval (bool, optional): Indicates whether multiple checkpoints may be evaluated in different
                processes at the same time, which is ``False``, by default.
        """

        # sanitize args
        insanity.sanitize_type("config_class", config_class, type)
        if not issubclass(training_class, training_executor.TrainingExecutor):
            raise ValueError("<training_class> has to be a subtype of expbase.training_executor.TrainingExecutor")
        if not issubclass(evaluation_class, evaluation_executor.EvaluationExecutor):
            raise ValueError("<evaluation_class> has to be a subtype of expbase.evaluation_executor.EvaluationExecutor")
        if not issubclass(config_class, base_config.BaseConfig):
            raise ValueError("<config_class> has to be a subtype of expbase.base_config.BaseConfig")

        # store provided args
        self._app_description = str(app_description)
        self._app_name = str(app_name)
        self._config_class = config_class
        self._evaluation_class = evaluation_class
        self._parallel_eval = bool(parallel_eval)
        self._training_class = training_class

        # create a parser that will be used for reading command-line args later
        self._arg_parser = argmagiq.MagiqParser(config_class, app_name, app_description)

    #  METHODS  ########################################################################################################

    def _create_evaluation_process(
            self,
            conf: base_config.BaseConfig,
            ctx: context.BaseContext,
            ckpt: typing.Optional[str]
    ) -> process.BaseProcess:
        """Creates a new process for running an evaluation executor.

        Args:
            conf (:class:`base_config.BaseConfig`): The user-defined configuration of the conducted experiment.
            ctx (context.BaseContext): The context for creating the process.
            ckpt (str): A string describing the checkpoint to evaluate or ``None`` if no checkpoint has been delivered

        Returns:
            process.BaseProcess: The created process, which has not been started yet.
        """

        return ctx.Process(
                target=self._launch_evaluation,
                args=(self._evaluation_class, conf, ckpt)
        )

    def _create_training_process(
            self,
            conf: base_config.BaseConfig,
            ctx: context.BaseContext,
            ckpt_queue: mp.Queue
    ) -> process.BaseProcess:
        """Creates a new process for running a training executor.

        Args:
            conf (:class:`base_config.BaseConfig`): The user-defined configuration of the conducted experiment.
            ctx (context.BaseContext): The context for creating the process.

        Returns:
            process.BaseProcess: The created process, which has not been started yet.
        """

        return ctx.Process(
                target=self._launch_training,
                args=(self._training_class, conf, ckpt_queue)
        )

    def _exit(self, message: str = None) -> None:
        """Prints a message, and exits the Python application.

        Notice:
            This method was chosen **not** to be static, as it may be overridden and need access to an instance of this
            class.

        Args:
            message (str, optional): The message to print before exiting.
        """

        if message is not None:
            print(message)
        sys.exit(0)

    @staticmethod
    def _launch_evaluation(eval_class: type, conf: base_config.BaseConfig, ckpt: typing.Optional[str]) -> None:
        """Used to launch the evaluation of a checkpoint in a new process.

        Cf. :meth:`_create_evaluation_process`.

        Args:
            eval_class (type): The implementation of :class:`evaluation_executor.EvaluationExecutor` to use.
            conf (:class:`base_config.BaseConfig`): The configuration of the conducted experiment.
            ckpt (str): A string describing the checkpoint to evaluate or ``None`` if no checkpoint has been delivered.
        """

        eval_class(conf, ckpt).run()

    @staticmethod
    def _launch_training(training_class: type, conf: base_config.BaseConfig, ckpt_queue: mp.Queue) -> None:
        """Used to launch the training procedure in a new process.

        Cf. :meth:`_create_training_process`.

        Args:
            training_class (type): The implementation of :class:`training_executor.TrainingExecutor` to use.
            conf (:class:`base_config.BaseConfig`): The configuration of the conducted experiment.
            ckpt_queue (mp.Queue): The queue that is used the communication between the controller and the training
                process.
        """

        training_class(conf, ckpt_queue).run()

    def _prepare_results_dir(self, conf: base_config.BaseConfig) -> None:
        """Prepares the directory for storing any results of the conducted experiment.

        This method performs the following three steps:
        1. It first examines whether the results directory that is specified in the provided configuration exists, and
           if this is not the case, then it creates the same.
        2. Next, it creates a subdirectory for the particular run of the experiment, which is named following the
           general pattern date-time[--title].
        3. Finally, the results directory in the configuration is updated to the run-specific one that was created in
           the previous step.

        Notice:
            This method was chosen **not** to be static, as it may be overridden and need access to an instance of this
            class.

        Args:
            conf (:class:`base_config.BaseConfig`): The configuration that has been provided for the conducted
                experiment.
        """

        # create results dir if it doesn't exist
        if not os.path.isdir(conf.results_dir):
            os.mkdir(conf.results_dir)

        # create experiment-specific results dir
        exp_results_dir = "{:%Y-%m-%d--%H-%M-%S}".format(datetime.datetime.now())
        if conf.title is not None:
            exp_results_dir += "--" + conf.title.replace(" ", "-")
        exp_results_dir = os.path.join(conf.results_dir, exp_results_dir)
        os.mkdir(exp_results_dir)

        # update results dir in config
        conf.results_dir = exp_results_dir

    def _print_config(self, conf: base_config.BaseConfig) -> None:
        """Prints details about the configuration that was provided for the conducted experiment.

        Args:
            conf (:class:`base_config.BaseConfig`): The configuration that has been provided for the conducted
                experiment.
        """

        # print the command that was used to run this application
        print("$", self._app_name, " ".join(sys.argv[1:]))
        print()

        # fetch configuration as sorted list of key-value pairs
        data = list(argmagiq.extract_config(conf).items())
        data.sort(key=(lambda x: x[0]))

        # print the configuration as table
        print(table.Table(title="CONFIGURATION").add(data))
        print()

    def _sanitize_config(self, conf: base_config.BaseConfig) -> None:
        """This method implements additional sanity checks that cannot be enforced during arg parsing.

        Args:
            conf (:class:`base_config.BaseConfig`): The configuration that was provided for the conducted experiment.
        """

        # if a test is being performed, then a training checkpoint that contains the model to use has to be provided
        if conf.test and conf.ckpt is None:
            raise ValueError("For running a test, an according training checkpoint has to be provided")

    def _store_config(self, conf: base_config.BaseConfig) -> None:
        """Stores the used configuration as JSON file in the results directory.

        Args:
            conf (:class:`base_config.BaseConfig`): The configuration that was provided for the conducted experiment.
        """

        # extract the configuration (as dict) from the config object
        conf_dict = argmagiq.extract_config(conf)

        # remove the run-specific directory that was added to the results directory again from the config to store
        conf_dict["results_dir"] = os.path.normpath(os.path.join(conf_dict["results_dir"], ".."))

        # write the config as JSON file to the results dir
        with open(os.path.join(conf.results_dir, "config.json"), "w") as f:
            json.dump(conf_dict, f, indent=4)

    def run(self):
        """Starts the experiment.

        This method first runs all of the necessary preparatory actions, and then launches the actual experiment.
        """

        # parse args + sanitize config
        try:

            conf = self._arg_parser.parse_args()
            if conf is None:  # -> the help text has been printed
                return
            self._sanitize_config(conf)

        except (TypeError, ValueError) as e:

            print(e)
            return

        # prepare the directory for storing results + store the used configuration
        self._prepare_results_dir(conf)
        self._store_config(conf)

        # redirect entire output to a log file
        streamtologger.redirect(
                target=os.path.join(conf.results_dir, conf.general_log),
                print_to_screen=(not conf.quiet),
                append=False,
                header_format=expbase.LOG_LINE_HEADER
        )

        # print the parsed configuration to the screen
        self._print_config(conf)

        # create context for creating multiprocessing objects
        ctx = mp.get_context(self.PROCESS_START_METHOD)

        # create a queue for receiving checkpoints from the training process
        ckpt_queue = ctx.Queue()

        if conf.test:

            # launch test of the model
            print("starting test...")
            test_process = self._create_evaluation_process(conf, ctx, None)
            test_process.start()

            # wait for test to finish
            test_process.join()
            print("finished test")

        else:

            # launch the training process
            training_process = self._create_training_process(conf, ctx, ckpt_queue)
            training_process.start()

            # as long as the training process is alive, wait for notifications about created checkpoints
            while training_process.is_alive() or not ckpt_queue.empty():

                try:

                    # fetch next checkpoint provided by the training process
                    ckpt = ckpt_queue.get(block=True, timeout=self.CHECK_ALIVE_INTERVAL)
                    print("retrieved checkpoint '{}'".format(ckpt))

                    # launch evaluation of the model stored in the retrieved checkpoint
                    print("starting evaluation...")
                    eval_process = self._create_evaluation_process(conf, ctx, ckpt)
                    eval_process.start()

                    # if parallel evaluation is not allowed, then wait for evaluation to end
                    if not self._parallel_eval:
                        eval_process.join()
                        print("finished evaluation")

                except queue.Empty:

                    pass  # nothing to do here -> check whether training process is still alive

        print("\n********** EXPERIMENT FINISHED **********")
