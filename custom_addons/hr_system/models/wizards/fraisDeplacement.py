from odoo import models, fields, api

class FraisDeplacementManager(models.TransientModel):
    _name = 'frais.deplacement.wizard.manager'
    _description = 'Manager Reject Demande Frais de Deplacement Wizard'

    message_refused_by_manager = fields.Text(string="Message", required=True)

    def action_reject(self):
        leave_request = self.env['frais.deplacement'].browse(self._context.get('active_id'))

        leave_request.message_refused_by_manager = self.message_refused_by_manager

        leave_request.send_manager_rejection_email()

        leave_request.state = 'manager_reject'

        return {'type': 'ir.actions.act_window_close'}

    
    

class FraisDeplacementChefManager(models.TransientModel):
    _name = 'frais.deplacement.wizard.chefmanager'
    _description = 'Chef Manager Reject Demande Frais de Deplacement Wizard'

    message_refused_by_manager_chef = fields.Text(string="Message", required=True)

    def action_reject(self):
        leave_request = self.env['frais.deplacement'].browse(self._context.get('active_id'))

        leave_request.message_refused_by_manager_chef = self.message_refused_by_manager_chef

        leave_request.send_manager_chef_rejection_email()

        leave_request.state = 'manager_chef_reject'

        return {'type': 'ir.actions.act_window_close'}


class FraisDeplacementHr(models.TransientModel):
    _name = 'frais.deplacement.wizard.hr'
    _description = 'Hr Reject Demande Frais de Deplacement Wizard'

    message_refused_by_hr = fields.Text(string="Message", required=True)

    def action_reject(self):
        leave_request = self.env['frais.deplacement'].browse(self._context.get('active_id'))

        leave_request.message_refused_by_hr = self.message_refused_by_hr

        leave_request.send_hr_rejection_email()

        leave_request.state = 'refused'

        return {'type': 'ir.actions.act_window_close'}


class FraisDeplacementFinance(models.TransientModel):
    _name = 'frais.deplacement.wizard.finance'
    _description = 'Finance Reject Demande Frais de Deplacement Wizard'

    message_refused_by_finance = fields.Text(string="Message", required=True)

    def action_reject(self):
        leave_request = self.env['frais.deplacement'].browse(self._context.get('active_id'))

        leave_request.message_refused_by_finance = self.message_refused_by_finance

        leave_request.send_finance_rejection_email()

        leave_request.state = 'finance_reject'

        return {'type': 'ir.actions.act_window_close'}
    
    



