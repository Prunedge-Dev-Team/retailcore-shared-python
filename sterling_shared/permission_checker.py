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

    def __init__(self, my_dict):
        for key in my_dict:
            setattr(self, key, my_dict[key])


class UserAuthMixin:

    @staticmethod
    def get_auth_user(request):
        token = request.META.get("HTTP_AUTHORIZATION")
        auth_service_url = os.getenv('AUTH_SERVICE_URL', 'http://localhost:10060')
        auth_decode_url = f'{auth_service_url}/api/v1/auth/token/decode/'
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer {}'.format(token),
            'Content-Type': 'application/json'
        }
        data = {'token': token}
        # try:
        #
        # except requests.ConnectionError as err:
        #     raise serializers.ValidationError(f"Cannot establish connection: {err}")
        # except requests.HTTPError as err:
        #     raise serializers.ValidationError(f"HTTP Error: {err}")
        # except Exception as err:
        #     raise serializers.ValidationError(f"Error occurred: {err}")
        print(auth_decode_url)
        try:

            res = requests.post(auth_decode_url, json=data, headers=headers)
        except Exception as e:
            print(e)
            print(str(e))

        print(res.text)
        print(res.content)
        print(res.json())
        user_data = json.loads(res.text)
        request.user = UserData(user_data)


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
        return self.queryset.filter(tenant=self.request.user.tenant)
