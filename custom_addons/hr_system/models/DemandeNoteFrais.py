from odoo import models, fields, api

class ExpenseRequest(models.Model):
    _name = 'expense.request'
    _description = 'Demande de notes de frais'

    user_id = fields.Many2one('res.users', string="Demandeur", required=True, default=lambda self: self.env.user)
    date = fields.Date(string="Date de Demande", required=True, default=fields.Date.context_today)
    amount = fields.Float(string='Montant en dirhams marocains', required=True)
    mission = fields.Text(string='Mission', required=True)
    expense_type = fields.Selection([
        ('transport', 'Transport'),
        ('accommodation', 'Hébergement'),
        ('meal', 'Repas'),
        ('other', 'Autre'),
    ], string='Type de frais')
    expense_type_id = fields.Many2one('type.frais', string='Type de frais', required=True)
    document_support = fields.Binary(string="document d'assistance")
    state = fields.Selection([
        ('pending', 'En attente'),
        ('manager_reject', 'Refusé par Manager'),
        ('manager_approval', 'Validé par Manager'),
        ('refused', 'Refusé par HR'),
        ('done', 'Validé par HR'),
    ], string="Statut", default='pending', track_visibility='onchange')


    message_refused_by_manager = fields.Text(string="Message du Manager", required=False)   
    message_refused_by_hr = fields.Text(string="Message du HR", required=False)


    def approved_by_hr(self):
        self.state = 'done'

    def approved_by_manager(self):
        self.state = 'manager_approval'
        
    def refused_by_hr(self):
        return {
            'name': 'Reject la Demande de note de frais',
            'type': 'ir.actions.act_window',
            'res_model': 'demande.note.frais.reject.hr.wizard',  # Your custom wizard model
            'view_mode': 'form',
            'target': 'new',  # Open the form in a modal popup
            'context': {'default_message_refused_by_hr': self.message_refused_by_hr},  # Pass current value, if any
        }

    def refused_by_manager(self):
        return {
            'name': 'Reject la Demande de note de frais',
            'type': 'ir.actions.act_window',
            'res_model': 'demande.note.frais.reject.manager.wizard',  # Your custom wizard model
            'view_mode': 'form',
            'target': 'new',  # Open the form in a modal popup
            'context': {'default_message_refused_by_manager': self.message_refused_by_manager},  # Pass current value, if any
        }
        

    def send_rejection_email_manager(self):
        print("send_rejection_email_manager")


    def send_rejection_email_hr(self):
        print("send_rejection_email_hr")


class TypeFrais(models.Model):
    _name = 'type.frais'
    _description = 'Type de frais'

    name = fields.Char(string="Type de frais")