from odoo import models, api, fields
from datetime import datetime, date


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.depends('birthday')
    def compute_employee_birthday(self):
        for rec in self:
            if rec.birthday:
                today = date.today()
                age = today.year - rec.birthday.year - (
                        (today.month, today.day) < (rec.birthday.month, rec.birthday.day))
                rec.employee_age = str(age)
            else:
                rec.employee_age = ''

    employee_age = fields.Char(string="Age", compute="compute_employee_birthday", store=True)

    def cron_customer_birthday_reminder(self):
        emp_list = self.env['hr.employee'].search([('birthday', '!=', False)])
        today = datetime.now().date()
        ctx = self._context.copy()
        email_temp = self.env.ref("employee_birthday_wishes.email_template_birthday")
        for emp in emp_list:
            birthday = emp.birthday
            if birthday.month == today.month and birthday.day == today.day:
                email_temp.with_context(ctx).send_mail(emp.id)
