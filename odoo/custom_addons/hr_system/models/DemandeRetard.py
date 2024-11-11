from odoo import models, fields
from datetime import datetime

class DeclarationRetard(models.Model):
    _name = 'declaration.retard'
    _description = 'Déclaration de retard'

    user_id = fields.Many2one('res.users', string="Demandeur", required=True, default=lambda self: self.env.user)
    date = fields.Datetime(string="Date et Heure", required=True, default=lambda self: datetime.now().replace(second=0, microsecond=0))
    reason = fields.Text(string="Raison", required=True)
    type_retard = fields.Selection([
        ('justifié', 'Justifié'),
        ('injustifié', 'Injustifié')
    ], string="Type de retard")

    type_retard_id = fields.Many2one('type.demande.retard', string="Type de retard", required=True)
    state = fields.Selection([
        ('pending', 'En attente'),
        ('manager_reject', 'Refusé par Manager'),
        ('manager_approval', 'Validé par Manager'),
        ('refused', 'Refusé par HR'),
        ('done', 'Validé par HR'),
    ], string="Statut", default='pending', track_visibility='onchange')
    
    message_refused_by_manager = fields.Text(string="Message du Manager", required=False)
    message_refused_by_hr = fields.Text(string="Message du HR", required=False)

    # Button actions for manager and HR

    def approved_by_hr(self):
        self.state = 'done'

    def approved_by_manager(self):
        self.state = 'manager_approval'
        
    def refused_by_hr(self):
        return {
            'name': 'Reject Demande Retard HR',
            'type': 'ir.actions.act_window',
            'res_model': 'demande.retard.reject.hr.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_leave_id': self.id},
        }

    def refused_by_manager(self):
        return {
            'name': 'Reject Demande Retard Manager',
            'type': 'ir.actions.act_window',
            'res_model': 'demande.retard.reject.manager.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_leave_id': self.id},
        }
        
    def send_rejection_email_manager(self):
        print("send_rejection_email_manager")

    
    def send_rejection_email_hr(self):
        print("send_rejection_email_hr")


class TypeDemandeRetard(models.Model):
    _name = 'type.demande.retard'
    _description = 'Type de demande de retard'

    name = fields.Char(string="Type de demande de retard")