from odoo import models, fields, api

class RejectDemenadeSorieManager(models.TransientModel):
    _name = 'demande.sortie.reject.hr'
    _description = 'Hr Reject Demande Sortie Wizard'

    message_refused_by_hr = fields.Text(string="Message du HR", required=True)

    def action_reject_hr(self):
        # Get the leave request record (you can pass the leave request id via context)
        leave_request = self.env['demande.sortie'].browse(self._context.get('active_id'))

        # Set the rejection message on the leave request
        leave_request.message_refused_by_hr = self.message_refused_by_hr

        # Call the method to send the rejection email
        leave_request.send_rejection_email_hr()

        # You can perform any other necessary actions, like changing the leave status to 'Rejected'
        leave_request.state = 'refused'

        # Optionally, close the wizard
        return {'type': 'ir.actions.act_window_close'}

    
    

