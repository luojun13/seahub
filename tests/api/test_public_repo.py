import json

import pytest
pytestmark = pytest.mark.django_db

from seaserv import seafile_api, ccnet_threaded_rpc

from seahub.test_utils import BaseTestCase
from mock import patch
from seahub.role_permissions.settings import DEFAULT_ENABLED_ROLE_PERMISSIONS


TEST_ADD_PUBLIC_ENABLED_ROLE_PERMISSIONS = {
    'default': {
        'can_add_repo': True,
        'can_add_group': True,
        'can_view_org': True,
        'can_add_public_repo': True,
        'can_use_global_address_book': True,
        'can_generate_share_link': True,
        'can_generate_upload_link': True,
        'can_send_share_link_mail': True,
        'can_invite_guest': False,
        'can_drag_drop_folder_to_sync': True,
        'can_connect_with_android_clients': True,
        'can_connect_with_ios_clients': True,
        'can_connect_with_desktop_clients': True,
        'can_export_files_via_mobile_client': True,
        'storage_ids': [],
        'role_quota': '',
        'can_use_wiki': True,
    },
    'guest': {
        'can_add_repo': False,
        'can_add_group': False,
        'can_view_org': False,
        'can_add_public_repo': False,
        'can_use_global_address_book': False,
        'can_generate_share_link': False,
        'can_generate_upload_link': False,
        'can_send_share_link_mail': False,
        'can_invite_guest': False,
        'can_drag_drop_folder_to_sync': False,
        'can_connect_with_android_clients': False,
        'can_connect_with_ios_clients': False,
        'can_connect_with_desktop_clients': False,
        'can_export_files_via_mobile_client': False,
        'storage_ids': [],
        'role_quota': '',
        'can_use_wiki': False,
    },
}


class RepoPublicTest(BaseTestCase):
    def setUp(self):
        from constance import config
        self.config = config

        self.repo_id = self.create_repo(name='test-admin-repo', desc='',
                                        username=self.admin.username,
                                        passwd=None)
        self.url = '/api2/shared-repos/%s/' % self.repo_id
        self.user_repo_url = '/api2/shared-repos/%s/' % self.repo.id

        self.config.ENABLE_USER_CREATE_ORG_REPO = 1

    def tearDown(self):
        self.remove_repo(self.repo_id)
        # clear cache between every test case to avoid config option cache issue
        self.clear_cache()

    def test_admin_can_set_pub_repo(self):
        self.login_as(self.admin)

        resp = self.client.put(self.url+'?share_type=public&permission=rw')
        self.assertEqual(200, resp.status_code)
        json_resp = json.loads(resp.content)
        assert 'success' in json_resp

    def test_admin_can_unset_pub_repo(self):
        seafile_api.add_inner_pub_repo(self.repo_id, "r")

        self.login_as(self.admin)

        resp = self.client.delete(self.url+'?share_type=public')
        self.assertEqual(200, resp.status_code)
        json_resp = json.loads(resp.content)
        assert 'success' in json_resp

    @patch('seahub.role_permissions.utils.ENABLED_ROLE_PERMISSIONS', TEST_ADD_PUBLIC_ENABLED_ROLE_PERMISSIONS)
    def test_user_can_set_pub_repo(self):
        self.login_as(self.user)

        resp = self.client.put(self.user_repo_url+'?share_type=public&permission=rw')
        self.assertEqual(200, resp.status_code)
        json_resp = json.loads(resp.content)
        assert 'success' in json_resp

    @patch('seahub.role_permissions.utils.ENABLED_ROLE_PERMISSIONS', DEFAULT_ENABLED_ROLE_PERMISSIONS)
    def test_user_can_not_set_pub_repo_when_add_public_disabled(self):
        self.login_as(self.user)

        resp = self.client.put(self.user_repo_url+'?share_type=public&permission=rw')
        self.assertEqual(403, resp.status_code)

    def test_admin_can_set_pub_repo_when_setting_disalbed(self):
        assert bool(self.config.ENABLE_USER_CREATE_ORG_REPO) is True
        self.config.ENABLE_USER_CREATE_ORG_REPO = False
        assert bool(self.config.ENABLE_USER_CREATE_ORG_REPO) is False

        self.login_as(self.admin)

        resp = self.client.put(self.url+'?share_type=public&permission=rw')
        self.assertEqual(200, resp.status_code)
        json_resp = json.loads(resp.content)
        assert 'success' in json_resp

    def test_user_can_not_set_pub_repo_when_setting_disalbed(self):
        assert bool(self.config.ENABLE_USER_CREATE_ORG_REPO) is True
        self.config.ENABLE_USER_CREATE_ORG_REPO = False
        assert bool(self.config.ENABLE_USER_CREATE_ORG_REPO) is False

        self.login_as(self.user)

        resp = self.client.put(self.user_repo_url+'?share_type=public&permission=rw')
        self.assertEqual(403, resp.status_code)
