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


"""This is a very simple example that illustrates the basic setup of an experiment using the package `expbase`.

This basic setup includes the following steps:
1. define a config class,
2. implement a `TrainingExecutor`,
3. implement an `EvaluationExecutor`, and
4. launch the experiment.
"""


import expbase as xb


__author__ = "Patrick Hohenecker"
__copyright__ = "Copyright (c) 2020, Patrick Hohenecker"
__license__ = "BSD-2-Clause"
__version__ = "0.1.0-rc.1"
__date__ = "22 Jul 2020"
__maintainer__ = "Patrick Hohenecker"
__email__ = "patrick.hohenecker@gmx.at"
__status__ = "Development"


# ==================================================================================================================== #
#  CONFIG                                                                                                              #
# ==================================================================================================================== #


class MyConfig(xb.BaseConfig):

    DEFAULT_MY_CONF = "Unknown"

    #  CONSTRUCTOR  ####################################################################################################

    def __init__(self):

        super().__init__()

        self._my_conf = self.DEFAULT_MY_CONF

    #  PROPERTIES  #####################################################################################################

    @property
    def my_conf(self) -> str:
        """str: This is some configuration of your experiment that the user defines as a command-line arg."""

        return self._my_conf

    @my_conf.setter
    def my_conf(self, my_conf: str) -> None:

        self._my_conf = str(my_conf)


# ==================================================================================================================== #
#  TRAINING EXECUTOR                                                                                                   #
# ==================================================================================================================== #


class MyTrainingExecutor(xb.TrainingExecutor):

    def _run_training(self) -> None:

        print("This is where the actual training procedure is implemented.")
        print("The user-defined config is accessed via self._conf.")
        print(f"For example, the config my_conf (with arg --my-conf) was set to '{self._conf.my_conf}'.")

        print()

        print("Every now and then (usually after every training epoch), we create a training checkpoint,")
        print("which should be stored in the results directory.")
        print("The path of the results directory is stored in the config at self._conf.results_dir.")
        print("For this experiment, the results directory was chosen to be:")
        print(self._conf.results_dir)

        print()

        print("To deliver a checkpoint, and kick of evaluation, we use self._deliver_ckpt.")
        print("As an example, we deliver a checkpoint 'test.ckpt'.")
        print("(Usually, we would of course create the checkpoint file in the results directory first).")

        self._deliver_ckpt("test.ckpt")

        print()

        print("Done.")


# ==================================================================================================================== #
#  EVALUATION EXECUTOR                                                                                                 #
# ==================================================================================================================== #


class MyEvaluationExecutor(xb.EvaluationExecutor):

    def _run_evaluation(self) -> None:

        print("This is where the evaluation procedure is implemented.")
        print("The checkpoint that the EvaluationExecutor was launched for is stored in self._ckpt.")
        print(f"In this particular case, the processed checkpoint is '{self._ckpt}'.")

        print()

        print("Done.")


# ==================================================================================================================== #
#  MAIN                                                                                                                #
# ==================================================================================================================== #


def main():

    xb.Experiment(
            MyTrainingExecutor,
            MyEvaluationExecutor,
            MyConfig,
            "run.sh",  # the name of the app printed in its synopsis
            "This is in example that illustrates the basic setup of an experiment using expbase."  # the app's help text
    ).run()


if __name__ == "__main__":

    main()
