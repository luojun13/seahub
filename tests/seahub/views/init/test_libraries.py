import json

from django.core.urlresolvers import reverse
import pytest
pytestmark = pytest.mark.django_db

from seahub.options.models import UserOptions
from seahub.test_utils import BaseTestCase
from mock import patch

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

class LibrariesTest(BaseTestCase):
    def setUp(self):
        self.url = reverse('libraries') + '?_old=1'
        from constance import config
        self.config = config

    def test_user_guide(self):
        self.login_as(self.user)
        username = self.user.username
        assert UserOptions.objects.get_default_repo(username) is None
        assert UserOptions.objects.is_user_guide_enabled(username) is True

        resp = self.client.get(self.url)
        self.assertEqual(200, resp.status_code)
        self.assertTemplateUsed(resp, 'libraries.html')
        assert resp.context['guide_enabled'] is True

        resp = self.client.get(self.url)
        assert resp.context['guide_enabled'] is False

        assert UserOptions.objects.get_default_repo(username) is not None
        assert UserOptions.objects.is_user_guide_enabled(username) is False

    @patch('seahub.role_permissions.utils.ENABLED_ROLE_PERMISSIONS', TEST_ADD_PUBLIC_ENABLED_ROLE_PERMISSIONS)
    def test_pub_repo_creation_config(self):
        self.clear_cache()

        # user
        self.login_as(self.user)

        self.config.ENABLE_USER_CREATE_ORG_REPO = 1
        assert bool(self.config.ENABLE_USER_CREATE_ORG_REPO) is True

        resp = self.client.get(self.url)
        self.assertEqual(200, resp.status_code)
        assert resp.context['can_add_public_repo'] is True

        self.config.ENABLE_USER_CREATE_ORG_REPO = 0
        assert bool(self.config.ENABLE_USER_CREATE_ORG_REPO) is False

        resp = self.client.get(self.url)
        self.assertEqual(200, resp.status_code)
        assert resp.context['can_add_public_repo'] is False

        # logout
        self.logout()

        # admin
        self.login_as(self.admin)

        self.config.ENABLE_USER_CREATE_ORG_REPO = 1
        assert bool(self.config.ENABLE_USER_CREATE_ORG_REPO) is True

        resp = self.client.get(self.url)
        self.assertEqual(200, resp.status_code)
        assert resp.context['can_add_public_repo'] is True

        self.config.ENABLE_USER_CREATE_ORG_REPO = 0
        assert bool(self.config.ENABLE_USER_CREATE_ORG_REPO) is False

        resp = self.client.get(self.url)
        self.assertEqual(200, resp.status_code)
        assert resp.context['can_add_public_repo'] is True

    def test_get_user_joined_groups(self):
        self.login_as(self.user)

        resp = self.client.get(self.url)

        self.assertEqual(200, resp.status_code)
        self.assertTemplateUsed(resp, 'libraries.html')
        assert len(resp.context['joined_groups']) > 0
