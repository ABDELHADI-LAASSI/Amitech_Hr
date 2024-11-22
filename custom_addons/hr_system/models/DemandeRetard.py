from odoo import models, fields, api
from datetime import datetime, time, timedelta
from odoo.exceptions import UserError

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
                # Add one hour to the recorded arrival time
                adjusted_arrival_time = record.time_darrive + timedelta(hours=1)

                # Get the work schedule (assuming calendar is linked to the employee/resource)
                work_schedule = self.env['resource.calendar'].search(
                    [('name', '=', 'Standard 40 hours/week')], limit=1
                )

                if work_schedule:
                    # Get the weekday as a string ('0' for Monday, '6' for Sunday)
                    weekday = str(adjusted_arrival_time.weekday())

                    # Find the attendance rules for this day
                    day_schedule = work_schedule.attendance_ids.filtered(lambda att: att.dayofweek == weekday)

                    if day_schedule:
                        # Extract the working hours for the day
                        work_start = datetime.combine(
                            adjusted_arrival_time.date(),
                            time(int(day_schedule[0].hour_from), int((day_schedule[0].hour_from % 1) * 60))
                        )
                        work_end = datetime.combine(
                            adjusted_arrival_time.date(),
                            time(int(day_schedule[2].hour_to), int((day_schedule[2].hour_to % 1) * 60))
                        )

                        # Break times (hardcoded for now, replace with actual break times if defined)
                        break_start = datetime.combine(
                            adjusted_arrival_time.date(),
                            time(int(day_schedule[1].hour_from), int((day_schedule[1].hour_from % 1) * 60))
                        )
                        break_end = datetime.combine(
                            adjusted_arrival_time.date(),
                            time(int(day_schedule[1].hour_to), int((day_schedule[1].hour_to % 1) * 60))
                        )

                        # Ensure the arrival time is within work limits
                        if adjusted_arrival_time.time() > work_end.time():
                            adjusted_arrival_time = work_end
                        if adjusted_arrival_time.time() < work_start.time():
                            record.phrase_du_retard = "Je ne suis pas en retard."
                            continue

                        # Calculate lateness duration
                        lateness_duration = adjusted_arrival_time - work_start

                        # Subtract break time if the arrival overlaps with the break
                        if adjusted_arrival_time > break_start and adjusted_arrival_time < break_end:
                            lateness_duration -= break_end - break_start

                        # Convert lateness duration to hours and minutes
                        total_seconds = lateness_duration.total_seconds()
                        hours, remainder = divmod(total_seconds, 3600)
                        minutes = remainder // 60

                        # Format the lateness phrase
                        record.phrase_du_retard = (
                            f"Je suis arrivé en RETARD de {int(hours)} h {int(minutes)} mn, "
                            f"soit à {adjusted_arrival_time.strftime('%H:%M')} h. "
                            "J’éviterai à l’avenir cette malencontreuse situation."
                        )
                    else:
                        # No work schedule for this day
                        raise UserError("Aucun horaire de travail n'est défini pour ce jour.")
                else:
                    # No work calendar found
                    raise UserError("Aucun calendrier de travail associé n'a été trouvé.")
            else:
                # No arrival time defined
                record.phrase_du_retard = "Heure d'arrivée non définie."

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

