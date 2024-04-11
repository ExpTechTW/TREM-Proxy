import os

from core.constants import core_constant
from core.CWAReportSQL import CWAReportSQL


def initialize_environment(*, quiet: bool = False):
    CWAReportSQL(initialize_environment=True)
    if not quiet:
        print('Initialized environment for {} in {}'.format(
            core_constant.NAME, os.getcwd()))
