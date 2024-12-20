from odoo import models, fields, api
from datetime import datetime, time, timedelta
from odoo.exceptions import ValidationError

class DemandeAbsence(models.Model):
    _name = 'demande.absence'
    _description = 'Demande de Absence'
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

    # Absence
    absence_start_time = fields.Datetime(string='Heure de début de l\'absence')
    absence_end_time = fields.Datetime(string='Heure de fin de l\'absence')
    phrase_du_absence = fields.Char(string='Phrase de l\'absence', compute='_compute_phrase_du_absence', store=True)


    message_refused_by_manager = fields.Text(string="Message du Manager", required=False)
    message_refused_by_hr = fields.Text(string="Message du HR", required=False)

    


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
                # Add one hour to start and end times
                adjusted_start_time = record.absence_start_time + timedelta(hours=1)
                adjusted_end_time = record.absence_end_time + timedelta(hours=1)

                if adjusted_start_time > adjusted_end_time:
                    raise ValidationError("L'heure de debut de l'absence doit etre avant l'heure de fin de l'absence")

                # Retrieve the work schedule from the resource calendar
                work_schedule = self.env['resource.calendar'].search(
                    [('name', '=', 'Standard 40 hours/week')], limit=1
                )

                if work_schedule:
                    # Get the weekday as a string ('0' for Monday, '6' for Sunday)
                    weekday = str(adjusted_start_time.weekday())

                    # Find the attendance rules for this day
                    day_schedule = work_schedule.attendance_ids.filtered(lambda att: att.dayofweek == weekday)

                    if day_schedule:
                        # Extract working hours for the day
                        work_start = datetime.combine(
                            adjusted_start_time.date(),
                            time(int(day_schedule[0].hour_from), int((day_schedule[0].hour_from % 1) * 60))
                        )
                        work_end = datetime.combine(
                            adjusted_start_time.date(),
                            time(int(day_schedule[-1].hour_to), int((day_schedule[-1].hour_to % 1) * 60))
                        )

                        # Break times (assumed as defined in the second attendance line for the day)
                        break_start = datetime.combine(
                            adjusted_start_time.date(),
                            time(int(day_schedule[1].hour_from), int((day_schedule[1].hour_from % 1) * 60))
                        ) if len(day_schedule) > 1 else None

                        break_end = datetime.combine(
                            adjusted_start_time.date(),
                            time(int(day_schedule[1].hour_to), int((day_schedule[1].hour_to % 1) * 60))
                        ) if len(day_schedule) > 1 else None

                        # Adjust start and end times to fit within work limits 

                        

                        if adjusted_start_time < work_start or adjusted_start_time > adjusted_end_time or adjusted_start_time > work_end:
                            adjusted_start_time = work_start
                            record.absence_start_time = adjusted_start_time - timedelta(hours=1)
                        if adjusted_end_time > work_end or adjusted_end_time < adjusted_start_time or adjusted_end_time < work_start:
                            adjusted_end_time = work_end
                            record.absence_end_time = adjusted_end_time - timedelta(hours=1)

                        # Calculate the absence duration
                        duration = adjusted_end_time - adjusted_start_time

                        # Subtract break time if the absence overlaps with the break
                        if break_start and adjusted_start_time < break_end and adjusted_end_time > break_start:
                            break_duration = min(adjusted_end_time, break_end) - max(adjusted_start_time, break_start)
                            duration -= break_duration

                        # Convert duration to hours and minutes
                        total_hours, remainder = divmod(duration.total_seconds(), 3600)
                        total_minutes = remainder // 60

                        # Format the phrase
                        record.phrase_du_absence = (
                            f"Je suis Obligé de m’absenter le {adjusted_start_time.strftime('%d/%m/%Y')} de "
                            f"{adjusted_start_time.strftime('%H:%M')} à {adjusted_end_time.strftime('%H:%M')} "
                            f"soit {int(total_hours)} h {int(total_minutes)} mn."
                        )
                    else:
                        # Display a popup message and reset the record
                        raise ValidationError("Aucun horaire de travail défini pour ce jour dans le calendrier.")

                else:
                    # Display a popup message and reset the record
                    raise ValidationError("Calendrier de travail non trouvé.")
            else:
                record.phrase_du_absence = ""

    def refused_by_manager(self):
        return {
            'name': 'Reject Demande Absence ',
            'type': 'ir.actions.act_window',
            'res_model': 'demande.absence.wizard.manager',  # Your custom wizard model
            'view_mode': 'form',
            'target': 'new',  # Open the form in a modal popup
            'context': {'default_message_refused_by_manager': self.message_refused_by_manager},  # Pass current value, if any     
        }

    def approved_by_manager(self):
        self.state = 'manager_approval'

        

    def refused_by_hr(self):
        return {
            'name': 'Reject Demande Absence ',
            'type': 'ir.actions.act_window',
            'res_model': 'demande.absence.wizard.manager',  # Your custom wizard model
            'view_mode': 'form',
            'target': 'new',  # Open the form in a modal popup
            'context': {'default_message_refused_by_hr': self.message_refused_by_hr},  # Pass current value, if any
        }

    def approved_by_hr(self):
        self.state = 'done'
    

    def send_rejection_email_manager(self):
        print("send_rejection_email")


    def send_rejection_email_hr(self):
        print("send_rejection_email_hr")

