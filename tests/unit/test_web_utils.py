# Copyright (c) 2013 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mock
import testtools

from stackalytics.dashboard import helpers
from stackalytics.dashboard import parameters


class TestWebUtils(testtools.TestCase):
    def setUp(self):
        super(TestWebUtils, self).setUp()

    def test_make_commit_message(self):
        message = '''
During finish_migration the manager calls initialize_connection but doesn't
update the block_device_mapping with the potentially new connection_info
returned.


Fixes bug 1076801
Change-Id: Ie49ccd2138905e178843b375a9b16c3fe572d1db'''

        module = 'test'

        record = {
            'message': message,
            'module': module,
        }

        expected = '''\
During finish_migration the manager calls initialize_connection but doesn't \
update the block_device_mapping with the potentially new connection_info \
returned.
Fixes bug <a href="https://bugs.launchpad.net/bugs/1076801" class="ext_link">\
1076801</a>
''' + (
            'Change-Id: <a href="https://review.openstack.org/#q,'
            'Ie49ccd2138905e178843b375a9b16c3fe572d1db,n,z" class="ext_link">'
            'Ie49ccd2138905e178843b375a9b16c3fe572d1db</a>')

        observed = helpers.make_commit_message(record)

        self.assertEqual(expected, observed,
                         'Commit message should be processed correctly')

    def test_make_commit_message_blueprint_link(self):
        message = '''
Implemented new driver for Cinder <:
Implements Blueprint super-driver
Change-Id: Ie49ccd2138905e178843b375a9b16c3fe572d1db'''

        module = 'cinder'

        record = {
            'message': message,
            'module': module,
        }

        expected = '''\
Implemented new driver for Cinder &lt;:
Implements Blueprint ''' + (
            '<a href="https://blueprints.launchpad.net/cinder/+spec/'
            'super-driver" class="ext_link">super-driver</a>' + '\n' +
            'Change-Id: <a href="https://review.openstack.org/#q,'
            'Ie49ccd2138905e178843b375a9b16c3fe572d1db,n,z" class="ext_link">'
            'Ie49ccd2138905e178843b375a9b16c3fe572d1db</a>')

        observed = helpers.make_commit_message(record)

        self.assertEqual(expected, observed,
                         'Commit message should be processed correctly')

    @mock.patch('stackalytics.dashboard.vault.get_vault')
    @mock.patch('stackalytics.dashboard.vault.get_user_from_runtime_storage')
    def test_make_page_title(self, user_patch, vault_patch):
        user_inst = {'user_name': 'John Doe'}
        module_inst = {'module_group_name': 'neutron'}

        self.assertEqual('OpenStack community contribution in all releases',
                         helpers.make_page_title('all', None, None, None))
        self.assertEqual('OpenStack community contribution in Havana release',
                         helpers.make_page_title('Havana', None, None, None))
        self.assertEqual('Mirantis contribution in Havana release',
                         helpers.make_page_title(
                             'Havana', None, 'Mirantis', None))
        self.assertEqual('John Doe contribution in Havana release',
                         helpers.make_page_title(
                             'Havana', None, None, user_inst))
        self.assertEqual(
            'John Doe (Mirantis) contribution to neutron in Havana release',
            helpers.make_page_title(
                'Havana', module_inst, 'Mirantis', user_inst))

    @mock.patch('flask.request')
    @mock.patch('stackalytics.dashboard.parameters.get_default')
    def test_parameters_get_parameter(self, get_default, flask_request):

        flask_request.args = mock.Mock()
        flask_request.args.get = mock.Mock(side_effect=lambda x: x)

        def make(values=None):
            def f(arg):
                return values.get(arg, None) if values else None
            return f

        get_default.side_effect = make()
        flask_request.args.get.side_effect = make({'param': 'foo'})
        self.assertEqual(['foo'], parameters.get_parameter(
            {'param': 'foo'}, 'param'))

        flask_request.args.get.side_effect = make({'param': 'foo'})
        self.assertEqual(['foo'], parameters.get_parameter({}, 'param'))

        flask_request.args.get.side_effect = make({'param': 'foo'})
        self.assertEqual([], parameters.get_parameter(
            {}, 'other', use_default=False))

        flask_request.args.get.side_effect = make({'params': 'foo'})
        self.assertEqual(['foo'], parameters.get_parameter(
            {}, 'param', plural_name='params'))

        flask_request.args.get.side_effect = make({})
        get_default.side_effect = make({'param': 'foo'})
        self.assertEqual(['foo'], parameters.get_parameter({}, 'param'))
        self.assertEqual([], parameters.get_parameter({}, 'other'))
