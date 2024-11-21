from odoo import models, fields, api
from datetime import datetime, time, timedelta

class DemandeRetard(models.Model):
    _name = 'demande.retard'
    _description = 'Demande de Retard'
    _rec_name = 'employee_id'
    
    employee_id = fields.Many2one('hr.employee', string="Demandeur", required=True, default=lambda self: self._get_employee_for_current_user())

    Motif_de_notification = fields.Selection([
        ('mission' , 'Mission'),
        ('contre_temps', 'Contre temps'),
        ('Obligation', 'Obligation')
    ] , string="Type de notification")

    mission_id = fields.Many2one(
        'ordre.mission', 
        string='Numéro de Mission', 
        domain="[('user_id', '=', uid)]"  # Assumes 'user_id' relates to the user who created the mission
    )
    mission_description = fields.Text(string="Description de la Mission" , related='mission_id.mission_description')

    reason = fields.Text(string="Motif", required=True)
    

    state = fields.Selection([
        ('pending', 'En attente'),
        ('manager_reject', 'Refusé par Manager'),
        ('manager_approval', 'Validaé par Manager'),
        ('refused', 'Refusé par HR'),
        ('done', 'Validaé par HR'),],
        string="Statut", default='pending', track_visibility='onchange'
    )

    type_deduction = fields.Selection(
        [
            ('conge', 'A déduire de mon congé'),
            ('salaire', 'A déduire de mon salaire'),
        ],
        string="Type de Déduction"  # Label for the fielddefault='conge',  # Default value (can be 'conge' or 'salaire')
    )


    # Retard
    time_darrive = fields.Datetime(string='Heure d\'arrivée', help='Temps d\'arrivée')
    phrase_du_retard = fields.Char(string='Phrase du retard', compute='_compute_phrase_du_retard', store=True)


    message_refused_by_manager = fields.Text(string="Message du Manager", required=False)
    message_refused_by_hr = fields.Text(string="Message du HR", required=False)

    




    @api.model
    def _get_employee_for_current_user(self):
        # Get the current user
        user = self.env.user
        
        # Check if the user has an associated employee record
        employee = self.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
        
        # If the user has an associated employee, return it, otherwise return False (or None)
        return employee.id if employee else False


    @api.depends('time_darrive')
    def _compute_phrase_du_retard(self):
        for record in self:
            if record.time_darrive:
               # Extract the arrival time and add one hour
                arrival_time = (datetime.combine(datetime.today(), record.time_darrive.time()) + timedelta(hours=1)).time()


                # Define reference times
                start_time = time(8, 0)
                end_time = time(17, 0)
                break_start = time(12, 0)
                break_end = time(13, 0)

                # Adjust the arrival time if it's after 17:00
                if arrival_time > end_time:
                    arrival_time = end_time

                # Check if arrival time is before the start time
                if arrival_time < start_time:
                    record.phrase_du_retard = "Je ne suis pas en retard."
                    continue

                # Calculate the total working hours (subtract break time if applicable)
                time_diff = (
                    datetime.combine(datetime.today(), arrival_time) -
                    datetime.combine(datetime.today(), start_time)
                )
                total_seconds = time_diff.total_seconds()

                # Subtract 1 hour for break time if it overlaps
                if arrival_time >= break_end:
                    total_seconds -= 3600

                # Convert time difference to hours and minutes
                hours, remainder = divmod(total_seconds, 3600)
                minutes = remainder // 60

                # Format the lateness phrase
                record.phrase_du_retard = (
                    f"Je suis Arrivé en RETARD de {int(hours)} h {int(minutes)} mn "
                    f"soit à {1+record.time_darrive.hour:02}h {record.time_darrive.minute:02}mn. "
                    "J’éviterai à l’avenir cette malencontreuse situation."
                )

    def refused_by_manager(self):
        return {
            'name': 'Reject Demande Retard',
            'type': 'ir.actions.act_window',
            'res_model': 'demande.retard.wizard.manager',  # Your custom wizard model
            'view_mode': 'form',
            'target': 'new',  # Open the form in a modal popup
            'context': {'default_message_refused_by_manager': self.message_refused_by_manager},  # Pass current value, if any
        }

    def approved_by_manager(self):
        self.state = 'manager_approval'

        

    def refused_by_hr(self):
        return {
            'name': 'Reject Demande Retard',
            'type': 'ir.actions.act_window',
            'res_model': 'demande.retard.wizard.hr',  # Your custom wizard model
            'view_mode': 'form',
            'target': 'new',  # Open the form in a modal popup
            'context': {'default_message_refused_by_hr': self.message_refused_by_hr},  # Pass current value, if any
        }

    def approved_by_hr(self):
        self.state = 'done'
    

    def send_manager_rejection_email(self):
        print("send_rejection_email")


    def send_rejection_email_hr(self):
        print("send_rejection_email_hr")

