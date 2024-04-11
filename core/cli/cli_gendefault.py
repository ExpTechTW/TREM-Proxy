import os

from core.CWAReportSQL import CWAReportSQL


def generate_default_stuffs(*, quiet: bool = False):
	CWAReportSQL(generate_default_only=True)
	if not quiet:
		print('Generated default configuration files in {}'.format(os.getcwd()))