import json
import os

from rest_framework.exceptions import PermissionDenied, AuthenticationFailed
import requests
from collections.abc import Mapping



class CaseInsensitiveDict(Mapping):
    def __init__(self, data):
        self._data = {key.lower(): value for key, value in data.items()}

    def __getitem__(self, key):
        return self._data[key.lower()]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)
    

def get_user_permissions(user):
    """
    Fetch all permissions a user has
    """
    if user.is_authenticated:
        return user.permissions
    raise AuthenticationFailed


def check_user_has_permissions(request, perms):
    user = request.user
    """
    Function to check if a user has any of the permissions passed.
    """
    user_permissions = get_user_permissions(user)

    def check_perm(perm_list):
        return any(_perm in perm_list for _perm in perms)

    if user.is_admin is False and perms and check_perm(user_permissions) is False:
        if user.is_admin is False and perms and check_perm(user_permissions) is False:
            http_headers = CaseInsensitiveDict(request.headers)

            if "X-S2S-Api-Key" in http_headers:
                third_party_url = (
                    os.getenv("AUTH_SERVICE_URL", "http://localhost:10050")
                    + "/api/v1/service-auth/verify-header-key/"
                )
                json_payload = json.dumps(
                    {"api_key": http_headers.get("X-S2S-Api-Key")}
                )
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": request.headers.get("Authorization"),
                }
                response = requests.post(
                    third_party_url, data=json_payload, headers=headers
                )
                if response.status_code == 200 and response.json()["success"]:
                    return True
        raise PermissionDenied


class PermissionMixin:
    """
    Custom Permission mixin
    """

    custom_permissions = None

    def check_permissions(self, request):
        check_user_has_permissions(request, self.get_custom_permissions())
        return super().check_permissions(request)

    def get_custom_permissions(self):
        return self.custom_permissions


class TenantMixin:
    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(tenant_id=self.request.user.tenant_id)
