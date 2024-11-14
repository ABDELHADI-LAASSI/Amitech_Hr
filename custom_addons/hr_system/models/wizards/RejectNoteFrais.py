from odoo import models, fields, api

class RejectRetardManager(models.TransientModel):
    _name = 'demande.note.frais.reject.manager.wizard'
    _description = 'Manager Reject Demande Retard Wizard'

    message_refused_by_manager = fields.Text(string="Message", required=True)

    def action_reject(self):
        # Get the leave request record (you can pass the leave request id via context)
        leave_request = self.env['expense.request'].browse(self._context.get('active_id'))

        # Set the rejection message on the leave request
        leave_request.message_refused_by_manager = self.message_refused_by_manager

        # Call the method to send the rejection email
        leave_request.send_rejection_email_manager()

        # You can perform any other necessary actions, like changing the leave status to 'Rejected'
        leave_request.state = 'manager_reject'

        # Optionally, close the wizard
        return {'type': 'ir.actions.act_window_close'}


class RejectNoteFraisHr(models.TransientModel):
    _name = 'demande.note.frais.reject.hr.wizard'
    _description = 'Hr Reject Demande Retard Wizard'

    message_refused_by_hr = fields.Text(string="Message", required=True)

    def action_reject(self):
        # Get the leave request record (you can pass the leave request id via context)
        leave_request = self.env['expense.request'].browse(self._context.get('active_id'))

        # Set the rejection message on the leave request
        leave_request.message_refused_by_hr = self.message_refused_by_hr

        # Call the method to send the rejection email
        leave_request.send_rejection_email_hr()

        # You can perform any other necessary actions, like changing the leave status to 'Rejected'
        leave_request.state = 'refused'

        # Optionally, close the wizard
        return {'type': 'ir.actions.act_window_close'}

    
    

    

