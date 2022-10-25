import json
import os

import requests
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, AuthenticationFailed


def get_user_permissions(user):
    """
    Fetch all permissions a user has
    """
    if user.is_authenticated:
        return user.permissions
    raise AuthenticationFailed


def check_user_has_permissions(user, perms):
    """
    Function to check if a user has any of the permissions passed.
    """
    user_permissions = get_user_permissions(user)

    def check_perm(perm_list):
        return any(_perm in perm_list for _perm in perms)

    if user.is_admin is False and perms and check_perm(user_permissions) is False:
        raise PermissionDenied


class UserData(object):
    is_authenticated = True

    def __init__(self, my_dict):
        for key in my_dict:
            setattr(self, key, my_dict[key])


class UserAuthMixin:

    @staticmethod
    def get_auth_user(request):
        if request.user.is_authenticated:
            return
        token = request.META.get("HTTP_AUTHORIZATION")
        if token is None:
            raise AuthenticationFailed
        token = token.split()
        if len(token) < 2:
            raise serializers.ValidationError("Token format error")
        token = token[1]
        auth_service_url = os.getenv('AUTH_SERVICE_URL', 'http://localhost:10060')
        auth_decode_url = f'{auth_service_url}/api/v1/auth/decode/'
        headers = {'Accept': 'application/json', 'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        data = {'token': token}
        try:
            res = requests.request(method="POST", url=auth_decode_url, json=data, headers=headers)

        except requests.ConnectionError as err:
            raise serializers.ValidationError(f"Cannot establish connection: {err}") from err

        except requests.HTTPError as err:
            raise serializers.ValidationError(f"HTTP Error: {err}") from err
        except Exception as err:
            raise serializers.ValidationError(f"Error occurred: {err}") from err

        if 200 <= res.status_code < 300:
            request.user = UserData(res.json())
        else:
            raise AuthenticationFailed


class PermissionMixin:
    """
    Custom Permission mixin
    """
    custom_permissions = None

    def check_permissions(self, request):
        UserAuthMixin.get_auth_user(request)
        check_user_has_permissions(request.user, self.get_custom_permissions())
        return super().check_permissions(request)

    def get_custom_permissions(self):
        return self.custom_permissions


class TenantMixin:
    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(tenant_id=self.request.user.tenant_id)
