from django import template
from rolepermissions.checkers import has_role

register = template.Library()

@register.filter
def user_has_role(user, role_name):
    return has_role(user, role_name)