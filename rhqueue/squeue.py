import getpass
import grp
import subprocess
from typing import List
from .datagrid import DataGridLine, DataGridHandler
from .printer import GridPrinter
from .functions import handle_slurm_output
from .servers import ServerSet


class SqueueDataGridHandler(DataGridHandler):
    def __init__(self):
        super().__init__()
        self.admin = grp.getgrnam("sudo").gr_mem
        self.user = getpass.getuser()

    @property
    def is_user_admin(self):
        return self.user in self.admin

    def cancel_job(self, job_id):
        if self.is_user_job(self.user, job_id):
            subprocess.call(["scancel {}".format(job_id)], shell=True)
        elif self.is_user_admin:
            subprocess.call(["sudo -u slurm scancel {}".format(job_id)],
                            shell=True)
        else:
            print("You do not have the permission to cancel that job")

    def print_vals(self, job_id=None, verbosity=None, columns=[]):
        if columns:
            self.print_info(columns)
        else:
            res = subprocess.run(f"scontrol show jobs {job_id}",
                                 shell=True,
                                 stdout=subprocess.PIPE)
            if res.returncode != 0:
                print("there was a problem getting the job")
            else:
                keys = [
                    "EligibleTime", "SubmitTime", "StartTime", "ExcNodeList",
                    "JobId", "JobName", "JobState", "StdOut", "UserId",
                    "WorkDir", "NodesList"
                ]
                output = self.from_id(job_id)
                output = output.get_from_keys(
                    keys) if verbosity < 2 else output.info
                GridPrinter([
                    sorted([list(j) for j in output.items()],
                           key=lambda x: x[0])
                ],
                            headers=[["Key", "Value"]],
                            title=f"Information about job:{job_id}")

    def print_info(self, columns):
        self.colmn_sort = [(idx, val) for idx, val in enumerate(columns)]
        vals = [self.running_items, self.queued_items]
        data = [[self._get_columns(value, columns) for value in items]
                for items in vals]
        headers = [columns] * len(data)
        GridPrinter(data,
                    title="Queue Information",
                    sections=["Running Items", "Items in Queue"],
                    headers=headers)

    def _get_columns(self, line: DataGridLine, columns) -> List[str]:
        return list(line.get_from_keys(columns).values())
