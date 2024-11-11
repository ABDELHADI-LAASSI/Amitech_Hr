from odoo import models, fields, api

class DemandeHoursSuppWizardManager(models.TransientModel):
    _name = 'demande.heures.sup.wizard.manager'
    _description = 'Hr Reject Wizard'

    message_refused_by_manager = fields.Text(string="Message", required=True)

    def action_reject(self):
        # Get the leave request record (you can pass the leave request id via context)
        leave_request = self.env['demande.heures.sup'].browse(self._context.get('active_id'))

        # Set the rejection message on the leave request
        leave_request.message_refused_manager = self.message_refused_by_manager

        # Call the method to send the rejection email
        leave_request.send_manager_rejection_email()

        # You can perform any other necessary actions, like changing the leave status to 'Rejected'
        leave_request.state = 'manager_reject'

        # Optionally, close the wizard
        return {'type': 'ir.actions.act_window_close'}

    
    


class DemandeHoursSuppWizardManager(models.TransientModel):
    _name = 'demande.heures.sup.wizard.hr'
    _description = 'Hr Reject Wizard'

    message_refused_by_hr = fields.Text(string="Message", required=True)

    def action_reject(self):
        # Get the leave request record (you can pass the leave request id via context)
        leave_request = self.env['demande.heures.sup'].browse(self._context.get('active_id'))

        # Set the rejection message on the leave request
        leave_request.message_refused_hr = self.message_refused_by_hr

        # Call the method to send the rejection email
        leave_request.send_hr_rejection_email()

        # You can perform any other necessary actions, like changing the leave status to 'Rejected'
        leave_request.state = 'refused'

        # Optionally, close the wizard
        return {'type': 'ir.actions.act_window_close'}

    
    



