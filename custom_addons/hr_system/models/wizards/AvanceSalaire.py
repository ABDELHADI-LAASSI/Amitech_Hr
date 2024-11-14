from odoo import models, fields, api

class AvanceSalaireManager(models.TransientModel):
    _name = 'avance.salaire.wizard.manager'
    _description = 'Manager reject demande avance salaire wizard'

    message_refused_by_manager = fields.Text(string="Message", required=True)

    def action_reject(self):
        leave_request = self.env['avance.salaire'].browse(self._context.get('active_id'))

        leave_request.message_refused_by_manager = self.message_refused_by_manager

        leave_request.send_manager_rejection_email()

        leave_request.state = 'manager_reject'

        return {'type': 'ir.actions.act_window_close'}

    
    

class AvanceSalaireChefManager(models.TransientModel):
    _name = 'avance.salaire.wizard.chefmanager'
    _description = 'Manager Chef reject demande avance salaire wizard'

    message_refused_by_manager_chef = fields.Text(string="Message", required=True)

    def action_reject(self):
        leave_request = self.env['avance.salaire'].browse(self._context.get('active_id'))

        leave_request.message_refused_by_manager_chef = self.message_refused_by_manager_chef

        leave_request.send_manager_chef_rejection_email()

        leave_request.state = 'manager_chef_reject'

        return {'type': 'ir.actions.act_window_close'}


class AvanceSalaireHr(models.TransientModel):
    _name = 'avance.salaire.wizard.hr'
    _description = 'Hr reject demande avance salaire wizard'

    message_refused_by_hr = fields.Text(string="Message", required=True)

    def action_reject(self):
        leave_request = self.env['avance.salaire'].browse(self._context.get('active_id'))

        leave_request.message_refused_by_hr = self.message_refused_by_hr

        leave_request.send_hr_rejection_email()

        leave_request.state = 'refused'

        return {'type': 'ir.actions.act_window_close'}


class AvanceSalaireFinance(models.TransientModel):
    _name = 'avance.salaire.wizard.finance'
    _description = 'Finance reject demande avance salaire wizard'

    message_refused_by_finance = fields.Text(string="Message", required=True)

    def action_reject(self):
        leave_request = self.env['avance.salaire'].browse(self._context.get('active_id'))

        leave_request.message_refused_by_finance = self.message_refused_by_finance

        leave_request.send_finance_rejection_email()

        leave_request.state = 'finance_reject'

        return {'type': 'ir.actions.act_window_close'}
    
    



