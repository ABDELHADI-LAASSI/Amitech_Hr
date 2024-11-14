from odoo import models, fields, api

class OrdreMission(models.Model):
    _name = 'ordre.mission'
    _description = 'Ordre de Mission'

    name = fields.Char(string="Nom de la Mission", required=True)
    user_id = fields.Many2one('res.users', string="Demandeur", required=True, default=lambda self: self.env.user)
    date = fields.Date(string="Date de Demande", required=True, default=fields.Date.context_today)
    montant = fields.Float(string="Montant en dirhams marocains", required=True)
    type_mission = fields.Selection([('locale', 'Locale'), ('internationale', 'Internationale')], string="Type de Mission")
    type_mission_id = fields.Many2one('type.mission', string='Type de Mission', required=True)
    mission_description = fields.Text(string="Description de la Mission")

    state = fields.Selection([
        ('pending', 'En attente'),
        ('manager_reject', 'Refusé par Manager'),
        ('manager_approval', 'Validé par Manager'),
        ('refused', 'Refusé par HR'),
        ('done', 'Validé par HR'),
    ], string="Statut", default='pending', track_visibility='onchange')

    # Méthodes de validation
    def approved_by_hr(self):
        self.state = 'done'

    def approved_by_manager(self):
        self.state = 'manager_approval'
    
    def refused_by_hr(self):
        self.state = 'refused'

    def refused_by_manager(self):
        self.state = 'manager_reject'
    

    def send_rejection_email_manager(self):
        print("send_rejection_email_manager")


    def send_rejection_email_hr(self):
        print("send_rejection_email_hr")


class TypeMission(models.Model):
    _name = 'type.mission'
    _description = 'Type de Mission'

    name = fields.Char(string="Type de Mission")