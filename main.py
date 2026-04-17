import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from utils import config_loader
from utils.logger import get_logger
from utils.system_info import get_system_info


def run_headless(export_fmt: str, output_path: str) -> int:
    from checkers.software_checker import SoftwareChecker
    from checkers.account_checker import AccountChecker
    from checkers.policy_checker import PolicyChecker
    from checkers.sensitive_checker import SensitiveChecker
    from utils import report_generator

    logger = get_logger()
    logger.info("Running in headless mode")
    system_info = get_system_info()

    checkers = [SoftwareChecker(), AccountChecker(), PolicyChecker(), SensitiveChecker()]
    results = []
    for checker in checkers:
        logger.info(f"Running {checker.__class__.__name__}…")
        result = checker.run()
        results.append(result)

    report_generator.generate(results, export_fmt, output_path, system_info)
    logger.info(f"Report saved to {output_path}")

    violations_total = sum(r.violation_count() for r in results)
    print(f"\nCheck complete. Total violations: {violations_total}")
    print(f"Report: {output_path}")
    return 1 if violations_total > 0 else 0


def run_gui():
    from PyQt5.QtWidgets import QApplication
    from ui.main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("终端安全合规检查工具")

    system_info = get_system_info()
    window = MainWindow(system_info)
    window.show()
    sys.exit(app.exec_())


def main():
    config_loader.load()

    parser = argparse.ArgumentParser(description="终端安全合规检查工具 / Security Compliance Checker")
    parser.add_argument("--headless", action="store_true", help="Run without GUI")
    parser.add_argument("--export", default="html", choices=["html", "txt", "excel", "pdf"],
                        help="Report format (headless mode only)")
    parser.add_argument("--output", default="security_report.html",
                        help="Output file path (headless mode only)")
    args = parser.parse_args()

    if args.headless:
        sys.exit(run_headless(args.export, args.output))
    else:
        run_gui()


if __name__ == "__main__":
    main()
