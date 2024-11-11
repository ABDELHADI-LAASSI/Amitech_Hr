from odoo import models, fields, api

class FraisDeplacement(models.Model):
    _name = 'frais.deplacement'
    _description = 'Remboursement des frais de déplacement'

    # Champs pour le demandeur
    user_id = fields.Many2one('res.users', string="Demandeur", required=True, default=lambda self: self.env.user)
    date = fields.Date(string="Date de Demande", required=True, default=fields.Date.context_today)
    montant = fields.Float(string="Montant en dirhams marocains", required=True)
    type_frais = fields.Selection([('transport', 'Transport'), ('hebergement', 'Hébergement'), ('nourriture', 'Nourriture')], string="Type de frais")
    type_frais_id = fields.Many2one('type.frais.deplacement', string='Type de frais de deplacement', required=True)
    
    mission = fields.Text(string="Mission", required=True)
    commentaire = fields.Text(string="Commentaires")

    # Champs de validation
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

    # Actions de validation pour chaque rôle

    def approved_by_manager(self):
        self.state = 'manager_approval'

    def refused_by_manager(self):
        return {
            'name': 'Reject la Demande de frais de deplacement',
            'type': 'ir.actions.act_window',
            'res_model': 'frais.deplacement.wizard.manager',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_leave_id': self.id},
        }

    def approved_by_manager_chef(self):
        self.state = 'manager_chef_approval'

    def refused_by_manager_chef(self):
        return {
            'name': 'Reject la Demande de frais de deplacement',
            'type': 'ir.actions.act_window',
            'res_model': 'frais.deplacement.wizard.chefmanager',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_leave_id': self.id},
        }

    def approved_by_hr(self):
        self.state = 'done'

    def refused_by_hr(self):
        return {
            'name': 'Reject la Demande de frais de deplacement',
            'type': 'ir.actions.act_window',
            'res_model': 'frais.deplacement.wizard.hr',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_leave_id': self.id},
        }
    
    def approved_by_finance(self):
        self.state = 'finance_approval'

    def refused_by_finance(self):
        return {
            'name': 'Reject la Demande de frais de deplacement',
            'type': 'ir.actions.act_window',
            'res_model': 'frais.deplacement.wizard.finance',
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
        # Check if the user is in the Manager group
        if self.env.user.has_group('hr_system.group_demande_sortie_manager'):
            # Extend the domain to filter by states using 'in'
            domain += [('state', 'in', ['pending', 'manager_approval', 'manager_reject'])]
        
        elif self.env.user.has_group('hr_system.group_demande_sortie_manager_2'):
            # Extend the domain for the second manager group
            domain += [('state', 'in', ['manager_approval', 'manager_chef_approval', 'manager_chef_reject'])]
        
        elif self.env.user.has_group('hr_system.group_demande_sortie_hr'):
            # Extend the domain for HR group
            domain += [('state', 'in', ['manager_chef_approval', 'done', 'refused'])]

        elif self.env.user.has_group('hr_system.group_demande_sortie_finance'):
            # Extend the domain for Finance group
            domain += [('state', 'in', ['finance_approval', 'finance_reject', 'done'])]
        
        # Call the super method with the modified domain
        res = super(FraisDeplacement, self)._search(domain, offset, limit, order, access_rights_uid)
        return res



class TypeFrais(models.Model):
    _name = 'type.frais.deplacement'
    _description = 'Type de frais de deplacement' 

    name = fields.Char(string="Type de frais de deplacement")