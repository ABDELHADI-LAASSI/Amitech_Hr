from odoo import models, fields
from datetime import datetime

class DemandeHeuresSup(models.Model):
    _name = 'demande.heures.sup'
    _description = 'Demandes d’approbation des heures supplémentaires'

    user_id = fields.Many2one('res.users', string="Demandeur", required=True, default=lambda self: self.env.user)
    date = fields.Datetime(string="Date et Heure", required=True, default=lambda self: datetime.now().replace(second=0, microsecond=0))
    type_heures_sup = fields.Selection([
        ('travail_extra', 'Travail Extra'),
        ('urgence', 'Urgence'),
        ('autre', 'Autre')
    ], string="Type d'Heures Supplémentaires")
    type_heures_sup_id = fields.Many2one('type.heures.sup', string="Type d'Heures Supplémentaires", required=True)
    nombre_heures = fields.Integer(string="Nombre d'heures", required=True)
    commentaires = fields.Text(string="Raison", required=True)
    
    state = fields.Selection([
        ('pending', 'En attente'),
        ('manager_reject', 'Refusé par Manager'),
        ('manager_approval', 'Validaé par Manager'),
        ('refused', 'Refusé par HR'),
        ('done', 'Validaé par HR'),],
        string="Statut", default='pending', track_visibility='onchange'
    )
    
    message_refused_manager = fields.Text(string="Message de refus du Manager", required=False)
    message_refused_hr = fields.Text(string="Message de refus des RH", required=False)

    # Actions pour le Manager et les RH
    def approved_by_manager(self):
        self.state = 'manager_approval'

    def refused_by_manager(self):
        return {
            'name': 'Reject Demande Heures Sup Manager',
            'type': 'ir.actions.act_window',
            'res_model': 'demande.heures.sup.wizard.manager',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_leave_id': self.id},
        }

    def approved_by_hr(self):
        self.state = 'done'

    def refused_by_hr(self):
        return {
            'name': 'Reject Demande Heures Sup hr',
            'type': 'ir.actions.act_window',
            'res_model': 'demande.heures.sup.wizard.hr',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_leave_id': self.id},
        }


    def send_manager_rejection_email(self):
        print("send_manager_rejection_email")

    def send_hr_rejection_email(self):
        print("send_manager_rejection_email")


class TypeHeuresSup(models.Model):
    _name = 'type.heures.sup'
    _description = 'Type d’Heures Supplémentaires'

    name = fields.Char(string="Type d'Heures Supplémentaires")