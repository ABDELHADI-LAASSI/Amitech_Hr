from odoo import models, fields, api
from datetime import datetime, time, timedelta
from odoo.exceptions import UserError , ValidationError
import logging
_logger = logging.getLogger(__name__)

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

                if adjusted_start_time > adjusted_end_time:
                    raise ValidationError("L'heure de debut de l'absence doit etre avant l'heure de fin de l'absence")

                # Get the work schedule (assuming calendar is linked to the employee/resource)
                work_schedule = self.env['resource.calendar'].search(
                    [('name', '=', 'Standard 40 hours/week')], limit=1
                )

                print(f"Adjusted Start Time: {adjusted_start_time}, Adjusted End Time: {adjusted_end_time}")

                if work_schedule:
                    # Get the weekday as a string ('0' for Monday, '6' for Sunday)
                    weekday = str(adjusted_start_time.weekday())

                    # Find the attendance rules for this day
                    day_schedule = work_schedule.attendance_ids.filtered(lambda att: att.dayofweek == weekday)

                    print(f"Day Schedule: {day_schedule}")

                    if day_schedule:
                        # Extract the working hours for the day
                        work_start = datetime.combine(
                            adjusted_start_time.date(),
                            time(int(day_schedule[0].hour_from), int((day_schedule[0].hour_from % 1) * 60))
                        )
                        work_end = datetime.combine(
                            adjusted_start_time.date(),
                            time(int(day_schedule[2].hour_to), int((day_schedule[2].hour_to % 1) * 60))
                        )

                        print(f"Work Start: {work_start}, Work End: {work_end}")

                        # Break times (hardcoded for now, replace with actual break times if defined)
                        break_start = datetime.combine(
                            adjusted_start_time.date(),
                            time(int(day_schedule[1].hour_from), int((day_schedule[1].hour_from % 1) * 60))
                        )
                        break_end = datetime.combine(
                            adjusted_start_time.date(),
                            time(int(day_schedule[1].hour_to), int((day_schedule[1].hour_to % 1) * 60))
                        )

                        # Ensure the times are within work limits
                        if adjusted_start_time < work_start or adjusted_start_time > adjusted_end_time or adjusted_start_time > work_end:
                            adjusted_start_time = work_start - timedelta(hours=1)
                        if adjusted_end_time > work_end or adjusted_end_time < adjusted_start_time or adjusted_end_time < work_start:
                            adjusted_end_time = work_end - timedelta(hours=1)

                        print(f"Adjusted Start: {adjusted_start_time}, Adjusted End: {adjusted_end_time}")

                        # Calculate the duration
                        duration = adjusted_end_time - adjusted_start_time
                        print(f"Initial Duration: {duration}")

                        # Subtract break time if the sortie overlaps with the break
                        if adjusted_start_time < break_end and adjusted_end_time > break_start:
                            break_duration = min(adjusted_end_time, break_end) - max(adjusted_start_time, break_start)
                            duration -= break_duration
                            print(f"Break Duration: {break_duration}, Final Duration: {duration}")

                        # Convert duration to hours and minutes
                        total_hours, remainder = divmod(duration.total_seconds(), 3600)
                        total_minutes = remainder // 60

                        # Format the phrase
                        record.phrase_du_sortie = (
                            f"Obligé de sortir le {adjusted_start_time.strftime('%d/%m/%Y')} à "
                            f"{adjusted_start_time.strftime('%H:%M')} h soit {int(total_hours)} h {int(total_minutes)} mn."
                        )
                    else:
                        raise UserError("Pas d'horaire prévu pour ce jour.")  # This will show a popup message
                else:
                    record.phrase_du_sortie = "Work calendar not found."
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


    @api.model
    def _get_employee_for_current_user(self):
        # Get the current user
        user = self.env.user
        
        # Check if the user has an associated employee record
        employee = self.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
        
        # If the user has an associated employee, return it, otherwise return False (or None)
        return employee.id if employee else False

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

