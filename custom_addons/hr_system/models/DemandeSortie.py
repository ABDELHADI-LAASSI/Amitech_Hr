from odoo import models, fields, api
from datetime import datetime

class DemandeSortie(models.Model):
    _name = 'demande.sortie'
    _description = 'Demande de sortie'
    
    user_id = fields.Many2one('res.users', string="Demandeur", required=True, default=lambda self: self.env.user)
    date = fields.Datetime(string="Date et Heure", required=True, default=lambda self: datetime.now().replace(second=0, microsecond=0))
    reason = fields.Text(string="Raison", required=True)
    duration = fields.Float(string="Durée (heures)", required=True)
    type_sortie = fields.Selection([
        ('personal', 'Personnel'),
        ('sick', 'Maladie'),
        ('emergency', 'Urgent'),
        ('business_trip', 'Déplacement Professionnel'),
        ('meeting', 'Réunion')
    ], string="Type de demande")

    type_sortie_id = fields.Many2one('type.demande.sortie', string="Type de demande", required=True)

    state = fields.Selection([
        ('pending', 'En attente'),
        ('manager_reject', 'Refusé par Manager'),
        ('manager_approval', 'Validaé par Manager'),
        ('refused', 'Refusé par HR'),
        ('done', 'Validaé par HR'),],
        string="Statut", default='pending', track_visibility='onchange'
    )
    message_refused_by_manager = fields.Text(string="Message du Manager", required=False)
    message_refused_by_hr = fields.Text(string="Message du HR", required=False)

    def refused_by_manager(self):
        return {
            'name': 'Reject Demande Sortie Manager',
            'type': 'ir.actions.act_window',
            'res_model': 'demande.sortie.reject.manager.wizard',  # Your custom wizard model
            'view_mode': 'form',
            'target': 'new',  # Open the form in a modal popup
            'context': {'default_message_refused_by_manager': self.message_refused_by_manager},  # Pass current value, if any
        }

    def approved_by_manager(self):
        self.state = 'manager_approval'

        

    def refused_by_hr(self):
        return {
            'name': 'Reject Demande Sortie HR',
            'type': 'ir.actions.act_window',
            'res_model': 'demande.sortie.reject.hr',  # Your custom wizard model
            'view_mode': 'form',
            'target': 'new',  # Open the form in a modal popup
            'context': {'default_message_refused_by_hr': self.message_refused_by_hr},  # Pass current value, if any
        }

    def approved_by_hr(self):
        self.state = 'done'
    

    def send_rejection_email(self):
        print("send_rejection_email")


    def send_rejection_email_hr(self):
        print("send_rejection_email_hr")


class TypeDemandeSortie(models.Model):
    _name = 'type.demande.sortie'
    _description = 'Type de demande de sortie'

    name = fields.Char(string="Type de demande")