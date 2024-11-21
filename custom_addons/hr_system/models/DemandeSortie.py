from odoo import models, fields, api
from datetime import datetime, time, timedelta

class DemandeSortie(models.Model):
    _name = 'demande.sortie'
    _description = 'Demande de sortie'
    _rec_name = 'employee_id'
    
    employee_id = fields.Many2one('hr.employee', string="Demandeur", required=True, default=lambda self: self._get_employee_for_current_user())


    Motif_de_notification = fields.Selection([
        ('mission' , 'Mission'),
        ('contre_temps', 'Contre temps'),
        ('Obligation', 'Obligation')
    ], string="Type de notification")

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

    # Sortie
    sortie_start_time = fields.Datetime(string='Heure de début de la sortie')
    sortie_end_time = fields.Datetime(string='Heure de fin de la sortie')
    phrase_du_sortie = fields.Char(string='Phrase de la sortie', compute='_compute_phrase_du_sortie', store=True)



    message_refused_by_manager = fields.Text(string="Message du Manager", required=False)
    message_refused_by_hr = fields.Text(string="Message du HR", required=False)

    



    @api.depends('sortie_start_time', 'sortie_end_time')
    def _compute_phrase_du_sortie(self):
        for record in self:
            if record.sortie_start_time and record.sortie_end_time:
                # Add one hour to the start and end times
                adjusted_start_time = record.sortie_start_time + timedelta(hours=1)
                adjusted_end_time = record.sortie_end_time + timedelta(hours=1)

                # Define work time limits
                work_start = datetime.combine(adjusted_start_time.date(), time(8, 0))
                work_end = datetime.combine(adjusted_start_time.date(), time(17, 0))
                break_start = datetime.combine(adjusted_start_time.date(), time(12, 0))
                break_end = datetime.combine(adjusted_start_time.date(), time(13, 0))

                # Ensure times are within work limits
                if adjusted_start_time < work_start:
                    adjusted_start_time = work_start
                if adjusted_end_time > work_end:
                    adjusted_end_time = work_end

                # Calculate the duration while accounting for the break time
                duration = adjusted_end_time - adjusted_start_time

                # Subtract break time if the sortie overlaps with the break
                if adjusted_start_time < break_end and adjusted_end_time > break_start:
                    break_duration = min(adjusted_end_time, break_end) - max(adjusted_start_time, break_start)
                    duration -= break_duration

                # Convert duration to hours and minutes
                total_hours, remainder = divmod(duration.total_seconds(), 3600)
                total_minutes = remainder // 60

                # Format the phrase
                record.phrase_du_sortie = (
                    f"Obligé de sortir le {adjusted_start_time.strftime('%d/%m/%Y')} à "
                    f"{adjusted_start_time.strftime('%H:%M')} h soit {int(total_hours)} h {int(total_minutes)} mn."
                )
            else:
                record.phrase_du_sortie = ""



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

