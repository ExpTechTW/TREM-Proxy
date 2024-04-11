import sys

from core.constants import core_constant
from core.CWAReportSQL import CWAReportSQL


def run():
	try:
		cwa_report_sql = CWAReportSQL()
	except Exception as e:
		print('Fail to initialize {}: ({}) {}'.format(core_constant.NAME, type(e), e), file=sys.stderr)
		raise

	if not cwa_report_sql.is_initialized():
		cwa_report_sql.run()
	else:
		pass