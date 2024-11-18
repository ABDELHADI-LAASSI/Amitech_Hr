from odoo import models, fields, api
from datetime import datetime, time, timedelta

class DemandeSortie(models.Model):
    _name = 'demande.sortie'
    _description = 'Demande de sortie'
    
    employee_id = fields.Many2one('hr.employee', string="Demandeur", required=True, default=lambda self: self._get_employee_for_current_user())

    date_from = fields.Datetime('Date Debut')
    date_to = fields.Datetime('Date Fin')


    Motif_de_notification = fields.Selection([
        ('mission' , 'Mission'),
        ('contre_temps', 'Contre temps'),
        ('Obligation', 'Obligation')
    ])

    mission_id = fields.Many2one(
        'ordre.mission', 
        string='Num Mission', 
        domain="[('user_id', '=', uid)]"  # Assumes 'user_id' relates to the user who created the mission
    )
    mission_description = fields.Text(string="Description de la Mission" , related='mission_id.mission_description')

    reason = fields.Text(string="Motif", required=True)
    duration = fields.Float(string="Durée (heures)", compute="_compute_duration" , required=True)
    
    my_selection_field = fields.Selection(
        [
            ('conge', 'A déduire de mon congé'),
            ('salaire', 'A déduire de mon salaire'),
        ],
        string="Type de Déduction",  # Label for the field
        default='conge',  # Default value (can be 'conge' or 'salaire')
    )

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

    type_demande = fields.Selection([
        ('retard', 'Retard'),
        ('absence', 'Absence'),
        ('sortie', 'Sortie'),
    ])


    # Retard
    time_darrive = fields.Datetime( string='Time of Arrival', help='Temps de darrive' )
    phrase_du_retard = fields.Char(string='Phrase du retard', compute='_compute_phrase_du_retard', store=True)

    # Absence
    absence_start_time = fields.Datetime(string='Start Time of Absence')
    absence_end_time = fields.Datetime(string='End Time of Absence')
    phrase_du_absence = fields.Char(string='Phrase du absence', compute='_compute_phrase_du_absence', store=True)


    # Sortie
    sortie_start_time = fields.Datetime(string='Start Time of Sortie')
    sortie_end_time = fields.Datetime(string='End Time of Sortie')
    phrase_du_sortie = fields.Char(string='Phrase du sortie', compute='_compute_phrase_du_sortie', store=True)


    message_refused_by_manager = fields.Text(string="Message du Manager", required=False)
    message_refused_by_hr = fields.Text(string="Message du HR", required=False)

    


    @api.depends('time_darrive')
    def _compute_phrase_du_retard(self):
        for record in self:
            if record.time_darrive:
                # Get the time part of the arrival time
                arrival_time = record.time_darrive.time()

                # Define the reference time (08:00)
                reference_time = time(8, 0)

                # Calculate the time difference between arrival and reference time
                if arrival_time >= reference_time:
                    time_diff = datetime.combine(datetime.today(), arrival_time) - datetime.combine(datetime.today(), reference_time)
                    

                    # Convert time difference to hours and minutes
                    hours, remainder = divmod(time_diff.total_seconds(), 3600)
                    minutes = remainder // 60

                    # Format the phrase
                    record.phrase_du_retard = (
                        f"Je suis Arrivé en RETARD de {int(hours)} h {int(minutes)} mn " 
                        f"soit à {1+record.time_darrive.hour:02}h {record.time_darrive.minute:02}mn. "
                        "J’éviterai à l’avenir cette malencontreuse situation."
                    )
                else:
                    # If arrival time is before 8:00, no phrase for being late
                    record.phrase_du_retard = "Je ne suis pas en retard."

    @api.depends('absence_start_time', 'absence_end_time')
    def _compute_absence_duration(self):
        for record in self:
            if record.absence_start_time and record.absence_end_time:
                duration = (record.absence_end_time - record.absence_start_time).total_seconds() / 3600.0
                record.absence_duration = duration


    @api.model
    def _get_employee_for_current_user(self):
        # Get the current user
        user = self.env.user
        
        # Check if the user has an associated employee record
        employee = self.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
        
        # If the user has an associated employee, return it, otherwise return False (or None)
        return employee.id if employee else False

    @api.depends('absence_start_time', 'absence_end_time')
    def _compute_phrase_du_absence(self):
        for record in self:
            if record.absence_start_time and record.absence_end_time:
                # Adjust times by adding 1 hour
                adjusted_start_time = record.absence_start_time + timedelta(hours=1)
                adjusted_end_time = record.absence_end_time + timedelta(hours=1)

                # Ensure that the start and end times are within the working hours
                if adjusted_start_time.hour < 8:
                    adjusted_start_time = adjusted_start_time.replace(hour=8, minute=0, second=0, microsecond=0)
                if adjusted_end_time.hour > 17:
                    adjusted_end_time = adjusted_end_time.replace(hour=17, minute=0, second=0, microsecond=0)

                # Calculate the duration between start and end times
                duration = adjusted_end_time - adjusted_start_time

                # Subtract the lunch break time (12:00 to 1:00)
                if adjusted_start_time.hour < 12 and adjusted_end_time.hour > 13:
                    break_time = timedelta(hours=1)
                    duration -= break_time

                total_hours, remainder = divmod(duration.total_seconds(), 3600)
                total_minutes = remainder // 60

                # Format the phrase
                record.phrase_du_absence = (
                    f"Je suis Obligé de m’absenter le {adjusted_start_time.strftime('%d/%m/%Y')} de "
                    f"{adjusted_start_time.strftime('%H:%M')} à {adjusted_end_time.strftime('%H:%M')} "
                    f"soit {int(total_hours)} h {int(total_minutes)} mn."
                )
            else:
                record.phrase_du_absence = ""


    @api.depends('sortie_start_time', 'sortie_end_time')
    def _compute_phrase_du_sortie(self):
        for record in self:
            if record.sortie_start_time and record.sortie_end_time:
                # Add one hour to the start and end times
                adjusted_start_time = record.sortie_start_time + timedelta(hours=1)
                adjusted_end_time = record.sortie_end_time + timedelta(hours=1)

                # Calculate the duration between adjusted start and end times
                duration = adjusted_end_time - adjusted_start_time
                total_hours, remainder = divmod(duration.total_seconds(), 3600)
                total_minutes = remainder // 60

                # Format the phrase
                record.phrase_du_sortie = (
                    f"Obligé de sortir le {adjusted_start_time.strftime('%d/%m/%Y')} à "
                    f"{adjusted_start_time.strftime('%H:%M')} h soit {int(total_hours)} h {int(total_minutes)} mn."
                )
            else:
                record.phrase_du_sortie = ""

    @api.depends('date_from', 'date_to')
    def _compute_duration(self):
        for record in self:
            if record.date_from and record.date_to:
                # Calculate duration in hours
                record.duration = (record.date_to - record.date_from).total_seconds() / 3600
            else:
                # Set duration to 0 or leave it as None if required
                record.duration = 0


    @api.depends('sortie_start_time', 'sortie_end_time')
    def _compute_sortie_duration_hours(self):
        for record in self:
            if record.sortie_start_time and record.sortie_end_time:
                # Calculate the time difference between start and end time
                start_time = fields.Datetime.from_string(record.sortie_start_time)
                end_time = fields.Datetime.from_string(record.sortie_end_time)

                # Calculate the difference and convert it to hours
                time_diff = end_time - start_time
                record.sortie_duration_hours = time_diff.total_seconds() / 3600  # Convert seconds to hours
            else:
                # If start or end time is not set, set duration to 0
                record.sortie_duration_hours = 0.0

    @api.depends('sortie_start_time', 'sortie_end_time')
    def _compute_sortie_duration_minutes(self):
        for record in self:
            if record.sortie_start_time and record.sortie_end_time:
                # Calculate the time difference between start and end time
                start_time = fields.Datetime.from_string(record.sortie_start_time)
                end_time = fields.Datetime.from_string(record.sortie_end_time)

                # Calculate the difference and convert it to minutes
                time_diff = end_time - start_time
                record.sortie_duration_minutes = (time_diff.total_seconds() / 60) % 60  # Convert seconds to minutes
            else:
                # If start or end time is not set, set duration to 0
                record.sortie_duration_minutes = 0.0

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

