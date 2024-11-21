from odoo import models, fields, api

class DemandeDocumentTravail(models.Model):
    _name = 'demande.document.travail'
    _description = 'Demande des Documents de Travail'

    # Demandeur Section
    user_id = fields.Many2one('res.users', string="Demandeur", required=True, default=lambda self: self.env.user)
    document_type = fields.Selection([
        ('contract', 'Contrat de Travail'),
        ('certificate', 'Certificat de Travail'),
        ('leave', 'Attestation de Congé')
    ], string="Type de Documents Demandés")

    document_type_id = fields.Many2one('type.document.travail', string="Type de Documents Demandés", required=True)

    # RH Section
    state = fields.Selection([
        ('pending', 'En attente'),
        ('refused', 'Refusé par HR'),
        ('done', 'Validé par HR'),
    ], string="Statut", default='pending', track_visibility='onchange')

    message_refused_by_hr = fields.Text(string="Commentaire HR")

    def approved_by_hr(self):
        self.state = 'done'
    
    def refused_by_hr(self):
        return {
            'name': "Reject la Demande d'avance sur Salaire",
            'type': 'ir.actions.act_window',
            'res_model': 'demande.document.wizard.hr',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_leave_id': self.id},
        }

    
    def send_rejection_email_hr(self):
        print("send_rejection_email_hr")
    

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):

        # ====================
        # add user domain to see only he's demande
        # ====================

        
        # Vérifiez si l'utilisateur appartient au groupe Hr
        
        if self.env.user.has_group('hr_system.group_demande_sortie_hr'):
            domain += [('state', 'in', ['pending', 'done', 'refused'])]

        # Appel de la méthode super avec le domaine modifié
        res = super(DemandeDocumentTravail, self)._search(domain, offset, limit, order, access_rights_uid)
        return res


class TypeDocumentTravail(models.Model):
    _name = 'type.document.travail'
    _description = 'Type de Document de Travail' 

    name = fields.Char(string="Type de Document de Travail")