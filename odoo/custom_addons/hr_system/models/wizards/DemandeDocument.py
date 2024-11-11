from odoo import models, fields, api

class DemandeDocumentHr(models.TransientModel):
    _name = 'demande.document.wizard.hr'
    _description = 'Hr Reject Demande Document Wizard'

    message_refused_by_hr = fields.Text(string="Message du HR", required=True)

    def action_reject(self):
        # Get the leave request record (you can pass the leave request id via context)
        leave_request = self.env['demande.document.travail'].browse(self._context.get('active_id'))

        # Set the rejection message on the leave request
        leave_request.message_refused_by_hr = self.message_refused_by_hr

        # Call the method to send the rejection email
        leave_request.send_rejection_email_hr()

        # You can perform any other necessary actions, like changing the leave status to 'Rejected'
        leave_request.state = 'refused'

        # Optionally, close the wizard
        return {'type': 'ir.actions.act_window_close'}

    
    

