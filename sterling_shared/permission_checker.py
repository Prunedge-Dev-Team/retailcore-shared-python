import json
import os

from rest_framework.exceptions import PermissionDenied, AuthenticationFailed
import requests


def get_user_permissions(user):
    """
    Fetch all permissions a user has
    """
    if user.is_authenticated:
        return user.permissions
    raise AuthenticationFailed


def check_user_has_permissions(request, perms, auth_service_url):
    user = request.user
    """
    Function to check if a user has any of the permissions passed.
    """
    user_permissions = get_user_permissions(user)

    def check_perm(perm_list):
        return any(_perm in perm_list for _perm in perms)

    if user.is_admin is False and perms and check_perm(user_permissions) is False:
        if 'X-Header-Service-Auth' in request.headers and auth_service_url:
            params = request.GET if request.method == 'GET' else request.POST
            third_party_url = auth_service_url + "/api/v1/service-auth/verify-header-key/"
            json_payload = json.dumps({'api_key': request.headers.get('X-Header-Service-Auth')})
            headers = {
                'Content-Type': 'application/json',
                'Authorization': request.headers.get('Authorization'),
            }
            response = requests.get(third_party_url, data=json_payload, headers=headers, params=params)
            if response.status_code == 200 and response.json()['success']:
                return True
        raise PermissionDenied


class PermissionMixin:
    """
    Custom Permission mixin
    """
    custom_permissions = None
    auth_service_url = None

    def check_permissions(self, request):
        check_user_has_permissions(request, self.get_custom_permissions(), self.auth_service_url)
        return super().check_permissions(request)

    def get_custom_permissions(self):
        return self.custom_permissions


class TenantMixin:
    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(tenant_id=self.request.user.tenant_id)
