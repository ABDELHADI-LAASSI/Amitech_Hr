from odoo import models, fields, api
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class GestionConge(models.Model):
    _name = 'gestion.conge'
    _description = 'Gestion des Congés'

    user_id = fields.Many2one('res.users', string="Demandeur", required=True, default=lambda self: self.env.user)
    date_from = fields.Date(string="Date de début", required=True)
    date_to = fields.Date(string="Date de fin", required=True)
    duree = fields.Integer(string="Durée (jour) ", compute="_compute_duree", store=True)
    type_conge = fields.Selection([
        ('maladie', 'Maladie'),
        ('autre', 'Autre'),
    ], string="Type de conge")
    type_conge_id = fields.Many2one('type.conge', string="Type de conge", required=True)
    description = fields.Text(string="Description")
    document_support = fields.Binary(string="document d'assistance")

    message_refused_by_manager = fields.Text(string="Message")
    message_refused_by_hr = fields.Text(string="Message")

    report_file = fields.Binary(string="Report Fichier")

    solde_restant = fields.Float(string="Solde Restant", compute="_compute_solde_restant")
    state = fields.Selection([
        ('pending', 'En attente'),
        ('manager_reject', 'Refusé par Manager'),
        ('manager_approval', 'Validaé par Manager'),
        ('refused', 'Refusé par HR'),
        ('done', 'Validaé par HR'),],
        string="Statut", default='pending', track_visibility='onchange'
    )
    
    @api.depends('date_from', 'date_to')
    def _compute_duree(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                delta = rec.date_to - rec.date_from
                rec.duree = delta.days + 1
            else:
                rec.duree = 0

    @api.depends('user_id')
    def _compute_solde_restant(self):
        # Placeholder for the leave balance calculation logic
        for rec in self:
            rec.solde_restant = 10  # Example static balance

    def action_manager_accept(self):
        # Update the state of the request
        self.state = 'manager_approval'

        # Get the email of the demandeur
        email = self.user_id.email

        # Check if the email is set
        if not email:
            raise UserError("Demandeur email is not set. Please provide a valid email to send the contract.")

        try:
            # Get the email template by reference
            template_id = self.env.ref('hr_system.conge_manager_accept_template').id
            template = self.env['mail.template'].browse(template_id)

            body_html = f"""
                            <div style="width:100%; display: flex; justify-content: center;">
                                <div style="color: black;">
                                    <h2>Dear <span>{self.user_id.name}</span>,</h2>
                                    <p>Your leave request from {self.date_from} to {self.date_to} has been accepted by the manager.</p>
                                    <p>Type of leave: {dict(self._fields['type_conge'].selection).get(self.type_conge)}</p>
                                </div>
                            </div>
                        """

            template.body_html = body_html

            # Send the email and capture the message ID
            message_id = template.send_mail(self.id, force_send=True)

            if message_id:
                _logger.info("Email sent successfully with message ID: %s", message_id)
            else:
                _logger.warning("Email send request was made, but no message ID was returned.")

        except Exception as e:
            _logger.error("Failed to send email: %s", e)



    def action_manager_reject(self):
        # Open a modal form to fill in the 'message_refused_by_manager' field
        return {
            'name': 'Reject Leave Request',
            'type': 'ir.actions.act_window',
            'res_model': 'gestion.conge.reject.wizard',  # Your custom wizard model
            'view_mode': 'form',
            'target': 'new',  # Open the form in a modal popup
            'context': {'default_message_refused_by_manager': self.message_refused_by_manager},  # Pass current value, if any
        }

    def send_rejection_email(self):
        # Get the email of the demandeur (the user who made the request)
        email = self.user_id.email

        # Check if the email is set; if not, raise an error
        if not email:
            raise UserError("Demandeur email is not set. Please provide a valid email to send the contract.")

        try:
            # Get the email template by reference
            template_id = self.env.ref('hr_system.conge_manager_accept_template').id
            template = self.env['mail.template'].browse(template_id)

            # Customize the email body with relevant information
            body_html = f"""
                <div style="width:100%; display: flex; justify-content: center;">
                    <div style="color: black;">
                        <h2>Dear <span>{self.user_id.name}</span>,</h2>
                        <p>Your leave request from {self.date_from} to {self.date_to} has been rejected by the manager.</p>
                        <p>Message: {self.message_refused_by_manager}</p>
                        <p>Type of leave: {dict(self._fields['type_conge'].selection).get(self.type_conge)}</p>
                    </div>
                </div>
            """

            # Update the email body in the template
            template.body_html = body_html

            # Send the email and capture the message ID
            message_id = template.send_mail(self.id, force_send=True)

            # Log whether the email was successfully sent or not
            if message_id:
                _logger.info("Email sent successfully with message ID: %s", message_id)
            else:
                _logger.warning("Email send request was made, but no message ID was returned.")

        except Exception as e:
            _logger.error("Failed to send email: %s", e)
            raise UserError(f"Failed to send email: {str(e)}")


    
    
    
    def action_hr_accept(self):
        self.state = 'done'

        # Get the email of the demandeur
        email = self.user_id.email

        # Check if the email is set
        if not email:
            raise UserError("Demandeur email is not set. Please provide a valid email to send the contract.")

        try:
            # Get the email template by reference
            template_id = self.env.ref('hr_system.conge_manager_accept_template').id
            template = self.env['mail.template'].browse(template_id)

            body_html = f"""
                                    <div style="width:100%; display: flex; justify-content: center;">
                                        <div style="color: black;">
                                            <h2>Dear <span>{self.user_id.name}</span>,</h2>
                                            <p>Your leave request from {self.date_from} to {self.date_to} has been accepted by the HR.</p>
                                            <p>Type of leave: {dict(self._fields['type_conge'].selection).get(self.type_conge)}</p>
                                        </div>
                                    </div>
                                """

            template.body_html = body_html

            # Send the email and capture the message ID
            message_id = template.send_mail(self.id, force_send=True)

            if message_id:
                _logger.info("Email sent successfully with message ID: %s", message_id)
            else:
                _logger.warning("Email send request was made, but no message ID was returned.")

        except Exception as e:
            _logger.error("Failed to send email: %s", e)


    def action_hr_reject(self):
        return {
            'name': 'Reject Leave Request by HR',
            'type': 'ir.actions.act_window',
            'res_model': 'gestion.conge.reject.wizard.hr',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_leave_id': self.id},
        }
    
    def send_hr_rejection_email(self):

        # Get the email of the demandeur
        email = self.user_id.email

        # Check if the email is set
        if not email:
            raise UserError("Demandeur email is not set. Please provide a valid email to send the contract.")

        try:
            # Get the email template by reference
            template_id = self.env.ref('hr_system.conge_manager_accept_template').id
            template = self.env['mail.template'].browse(template_id)

            body_html = f"""
                                    <div style="width:100%; display: flex; justify-content: center;">
                                        <div style="color: black;">
                                            <h2>Dear <span>{self.user_id.name}</span>,</h2>
                                            <p>Your leave request from {self.date_from} to {self.date_to} has been refused by the HR.</p>
                                            <p>Type of leave: {dict(self._fields['type_conge'].selection).get(self.type_conge)}</p>
                                        </div>
                                    </div>
                                """

            template.body_html = body_html

            # Send the email and capture the message ID
            message_id = template.send_mail(self.id, force_send=True)

            if message_id:
                _logger.info("Email sent successfully with message ID: %s", message_id)
            else:
                _logger.warning("Email send request was made, but no message ID was returned.")

        except Exception as e:
            _logger.error("Failed to send email: %s", e)
        







class TypeConge(models.Model):
    _name = 'type.conge'
    _description = 'Type de conge'

    name = fields.Char(string="Type de conge")