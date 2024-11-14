from odoo import models, fields

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    

    def download_report(self):
        report_action = self.env.ref('hr_system.model_hr_leave_report')
        print(report_action)
        return report_action.report_action(self)

    def send_report(self):
        print("send_report")
