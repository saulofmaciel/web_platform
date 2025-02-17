from rolepermissions.roles import AbstractUserRole

class Approver(AbstractUserRole):
    role_name = "approver"
    available_permissions = {
        'approver' : True,
        'internal_resource' : True
    }

class SiteAdmin(AbstractUserRole):
    role_name = 'site_admin'
    available_permissions = {
        'site_admin' : True
    }

class InternalResource(AbstractUserRole):
    role_name = 'internal_resource'
    available_permissions = {
        'internal_resource' : True
    }

class CertificateAdmin(AbstractUserRole):
    role_name = 'certificate_admin'
    available_permissions = {
        'certificate_admin' : True
    }
