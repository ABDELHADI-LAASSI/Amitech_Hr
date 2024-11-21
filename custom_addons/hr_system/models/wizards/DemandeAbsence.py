from odoo import models, fields, api

class DemandeAbsenceManager(models.TransientModel):
    _name = 'demande.absence.wizard.manager'
    _description = "Manager Reject Demande d'Absence Wizard"

    message_refused_by_manager = fields.Text(string="Message", required=True)

    def action_reject_manager(self):
        leave_request = self.env['demande.absence'].browse(self._context.get('active_id'))

        leave_request.message_refused_by_manager = self.message_refused_by_manager

        leave_request.send_rejection_email_manager()

        leave_request.state = 'manager_reject'

        return {'type': 'ir.actions.act_window_close'}

    
    

class DemandeAbsencedHr(models.TransientModel):
    _name = 'demande.absence.wizard.hr'
    _description = "Hr Reject Demande d'Absence Wizard"

    message_refused_by_hr = fields.Text(string="Message", required=True)

    def action_reject_hr(self):
        leave_request = self.env['demande.absence'].browse(self._context.get('active_id'))

        leave_request.message_refused_by_hr = self.message_refused_by_hr

        leave_request.send_rejection_email_hr()

        leave_request.state = 'refused'

        return {'type': 'ir.actions.act_window_close'}

