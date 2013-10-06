CS61AS edX Autograder
=====================

A fork of [https://github.com/Stanford-Online/xqueue_pull_ref](https://github.com/Stanford-Online/xqueue_pull_ref).

Interfaces the CS61AS Scheme Autograder with the [edX](https://www.edx.org/) system.
Dependencies (based on what is available on the Berkeley lab computers):
- Python 2.6
- requests
- grader (autograder command line tool for CS61AS)

Also note that an additional `config.py` file is needed with the queue authentication information.

Start the grader with

    python grader.py
