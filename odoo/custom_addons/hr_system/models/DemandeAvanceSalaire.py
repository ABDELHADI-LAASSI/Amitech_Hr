from odoo import models, fields, api

class AvanceSalaire(models.Model):
    _name = "avance.salaire"
    _description = "Demande d’Avance sur Salaire"

    # Informations de la demande
    user_id = fields.Many2one('res.users', string="Demandeur", required=True, default=lambda self: self.env.user)
    date = fields.Date(string="Date de Demande", required=True, default=fields.Date.context_today)
    montant = fields.Float(string="Montant en Dirhams", required=True)
    type_avance = fields.Selection([
        ('avance_salaire', 'Avance sur Salaire'),
        ('autre', 'Autre')  # Ajoutez d'autres types si nécessaire
    ], string="Type d'Avance")
    type_avance_id = fields.Many2one('type.avance.salaire', string='Type d\'Avance', required=True)
    numero_ordre_mission = fields.Char(string="Numéro d'Ordre de Mission", help="Référence de l'ordre de mission lié")

    # Statuts
    state = fields.Selection([
        ('pending', 'En attente'),
        ('manager_reject', 'Refusé par Manager'),
        ('manager_approval', 'Validé par Manager'),
        ('manager_chef_reject', 'Refusé par Manager Chef'),
        ('manager_chef_approval', 'Validé par Manager Chef'),
        ('refused', 'Refusé par HR'),
        ('done', 'Validé par HR'),
        ('finance_reject', 'Refusé par Finance'),
        ('finance_approval', 'Validé par Finance'),
    ], string="Statut", default='pending', track_visibility='onchange')

    # Champs pour les messages de refus
    message_refused_by_manager = fields.Text(string="Commentaire Manager")
    message_refused_by_manager_chef = fields.Text(string="Commentaire Manager Chef")
    message_refused_by_hr = fields.Text(string="Commentaire HR")
    message_refused_by_finance = fields.Text(string="Commentaire Finance")

    # Boutons pour les actions de validation et de refus
    def approved_by_manager(self):
        self.state = 'manager_approval'
    
    def refused_by_manager(self):
        return {
            'name': "Reject la Demande d'avance sur Salaire",
            'type': 'ir.actions.act_window',
            'res_model': 'avance.salaire.wizard.manager',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_leave_id': self.id},
        }
    
    def approved_by_manager_chef(self):
        self.state = 'manager_chef_approval'
    
    def refused_by_manager_chef(self):
        return {
            'name': "Reject la Demande d'avance sur Salaire",
            'type': 'ir.actions.act_window',
            'res_model': 'avance.salaire.wizard.chefmanager',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_leave_id': self.id},
        }
    
    def approved_by_hr(self):
        self.state = 'done'
    
    def refused_by_hr(self):
        return {
            'name': "Reject la Demande d'avance sur Salaire",
            'type': 'ir.actions.act_window',
            'res_model': 'avance.salaire.wizard.hr',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_leave_id': self.id},
        }
    
    def approved_by_finance(self):
        self.state = 'finance_approval'
    
    def refused_by_finance(self):
        return {
            'name': "Reject la Demande d'avance sur Salaire",
            'type': 'ir.actions.act_window',
            'res_model': 'avance.salaire.wizard.finance ',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_leave_id': self.id},
        }

    def send_manager_rejection_email(self):
        print("send_manager_rejection_email")
    
    def send_manager_chef_rejection_email(self):
        print("send_manager_chef_rejection_email")
    
    def send_hr_rejection_email(self):
        print("send_hr_rejection_email")


    def send_finance_rejection_email(self):
        print("send_finance_rejection_email")
    
    

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        # Vérifiez si l'utilisateur appartient au groupe Manager
        if self.env.user.has_group('hr_system.group_demande_sortie_manager'):
            domain += [('state', 'in', ['pending', 'manager_approval', 'manager_reject'])]
        
        elif self.env.user.has_group('hr_system.group_demande_sortie_manager_2'):
            domain += [('state', 'in', ['manager_approval', 'manager_chef_approval', 'manager_chef_reject'])]
        
        elif self.env.user.has_group('hr_system.group_demande_sortie_hr'):
            domain += [('state', 'in', ['manager_chef_approval', 'done', 'refused'])]

        elif self.env.user.has_group('hr_system.group_demande_sortie_finance'):
            domain += [('state', 'in', ['finance_approval', 'finance_reject', 'done'])]
        
        # Appel de la méthode super avec le domaine modifié
        res = super(AvanceSalaire, self)._search(domain, offset, limit, order, access_rights_uid)
        return res
    


class TypeAvanceSalaire(models.Model):
    _name = 'type.avance.salaire'
    _description = 'Type d’Avance Salaire' 

    name = fields.Char(string="Type d'Avance Salaire")