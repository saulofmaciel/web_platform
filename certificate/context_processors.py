from rolepermissions.checkers import get_user_roles

def user_roles(request):
    if request.user.is_authenticated:
        roles = [role.role_name for role in get_user_roles(request.user)]
    else:
        roles = []
    return {'user_roles': roles}
