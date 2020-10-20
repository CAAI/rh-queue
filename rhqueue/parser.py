import argparse
import os
from rhqueue.actions import FooAction
from .scriptCreator import ScriptCreatorClass
import sys
from .functions import *


class RHQueueParser(object):
  def __init__(self, **kwargs):
    argv = kwargs.get("argv", sys.argv[1:])
    argv = argv.split() if isinstance(argv, str) else argv
    # Main Parser
    self.parser = argparse.ArgumentParser(description="RHQueue",
                                          add_help=False)
    subparsers = self.parser.add_subparsers(
        help="The subcommand to run options are {queue,remove,info}",
        dest="command")

    # Queue Parser
    parser_queue = subparsers.add_parser("queue", help="Used to queue scripts")
    group = parser_queue.add_mutually_exclusive_group()
    parser_queue.add_argument("script",
                              metavar="script",
                              type=str,
                              help="""
          The script to run on a gpu.
          At the top of each file there must be the shebang '#!/usr/bin/env <python_version>'
          Where <python_version> is the version of python needed, python(for 2.7) or python3
        """)
    # venv defaults
    venv = os.environ.get("RHQ_VENV", "")
    venv = os.environ.get("VIRTUAL_ENV", venv)
    group.add_argument("-v",
                       "--venv",
                       metavar="venv",
                       type=str,
                       help="""
          The virtual environment used for the project. 
          The value is the absolute path to the virtual environment directoy
        """,
                       default=venv)
    group.add_argument("-c",
                       "--conda-venv",
                       metavar="condaVenv",
                       type=str,
                       help="""
        The environment for conda. 
        This is supposed to be the name of the conda environment.
      """,
                       default=os.environ.get("RHQ_CONDA_VENV", ""))

    parser_queue.add_argument("--source-script",
                              type=str,
                              help="""
        A script that is run before setting the virtual environment
                              """)

    parser_queue.add_argument(
        "-p",
        "--priority",
        type=str,
        choices=["1", "2", "3", "4", "5"],
        default="3",
        help="The priority of the script" +
        "\nDO NOT DEFINE UNLESS YOU ARE SURE THAT YOU DO NOT NEED HIGHER PRIORITY."
    )

    parser_queue.add_argument("-e",
                              "--email",
                              type=str,
                              help="""
          The email to send to when the script begins and ends.
          Can be defined as environment variable (export RHQ_EMAIL=<email>) to use as a default.
          This will prefer the email given in the argument line over the environtment variable
        """,
                              default=os.environ.get("RHQ_EMAIL", ""))

    parser_queue.add_argument("-o",
                              "--output-file",
                              type=str,
                              default="my.stdout",
                              help="""
          The file for the output of the script.
          This is the path to the file.
          Default is 'my.stdout'
        """)
    parser_queue.add_argument("-b",
                              "--begin-time",
                              type=parse_time,
                              help="Begin script after (b) seconds")

    parser_queue.add_argument(
        "-s",
        "--servers",
        type=ServerSet.from_slurm_list,
        help="Define the servers that the script can run on.")
    parser_queue.add_argument("-a",
                              "--args",
                              help="""
        The arguments for the script. 
        These are passed to the script to run.
        Pass these in the same method as you would normally
      """,
                              default=[],
                              nargs="+")
    parser_queue.add_argument("--test",
                              help="script is a test. Ignore this",
                              action="store_true",
                              default=False)
    parser_queue.add_argument(
        "--script-name",
        help="The name of the script file name that is inserted into the queue",
        action=FooAction)
    self.parser.add_argument("-h", action="help", help="print basic help")
    self.parser.add_argument("--help",
                             action="store_true",
                             help="print extended help")
    # Remove Subparser
    parser_remove = subparsers.add_parser("remove", help="remove help")
    parser_remove.add_argument("job",
                               help="the job id of the job to cancel",
                               type=int)

    parser_info = subparsers.add_parser("info", help="info help")
    parser_info.add_argument(
        "--job-id", "-j", help="the job id to get further information about")
    parser_info.add_argument("-v",
                             "--verbosity",
                             help="the level of verbosity",
                             type=int,
                             choices=[1, 2],
                             default=1)
    args = self.parser.parse_args(argv)

    if args.help:
      self.parser.print_help()
      print("Queue sub-command")
      parser_queue.print_help()
      print("Remove sub-command")
      parser_remove.print_help()
      print("Info sub-command")
      parser_info.print_help()
      exit(1)
    setattr(
        args, "script_name",
        args.script_name if hasattr(args, "script_name") and args.script_name
        else args.script if hasattr(args, "script") and args.script else "")
    self.args = args