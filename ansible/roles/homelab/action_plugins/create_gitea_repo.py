#!/usr/bin/python
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import logging
from time import sleep
import urllib3
from urllib3.util import Retry

from ansible.plugins.action import ActionBase
import gitea_api
from gitea_api.rest import ApiException

# Make urllib a little quieter
urllib3.disable_warnings()
logging.captureWarnings(True)


class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None):
        result = super(ActionModule, self).run(tmp, task_vars)
        args = self._task.args

        # Get the parameters
        gitea_host = args.get('host')
        gitea_username = args.get('username')
        gitea_password = args.get('password')
        repo_name = args.get('repo_name')
        repo_description = args.get('repo_description')
        private = args.get('private')

        configuration = gitea_api.Configuration()
        configuration.host = f'{gitea_host}/api/v1'
        configuration.verify_ssl = False
        configuration.username = gitea_username
        configuration.password = gitea_password

        api_instance = gitea_api.UserApi(
            gitea_api.ApiClient(configuration))

        # Need to apply a custom Retry object
        api_instance.api_client.rest_client.pool_manager.connection_pool_kw[
            'retries'] = Retry(total=10, backoff_factor=10)

        success = False
        new_repo = None
        for i in range(10):
            try:
                new_repo = api_instance.create_current_user_repo(
                    body=gitea_api.CreateRepoOption(
                        name=repo_name,
                        description=repo_description,
                        private=private))
                success = True
                result['msg'] = f"Repository {repo_name} created successfully"
                result['changed'] = True
                result['clone_url'] = new_repo.clone_url
                break
            except ApiException as e:
                if e.reason == "Service Temporarily Unavailable":
                    print("Waiting for Gitea to become available...")
                elif e.reason == "Conflict":  # Pre-existing repo is good enough for now
                    success = True
                    result['msg'] = f"Repository {repo_name} created successfully"
                    result['changed'] = False
                    result['clone_url'] = f"{gitea_host}/{gitea_username}/{repo_name}.git"
                    break
                elif e.reason == "Unauthorized":
                    result['msg'] = f"Could not authenticate."
                    break
                else:
                    print("Exception when calling "
                        "RepositoryApi->create_current_user_repo: %s\n" % e)
            print("Sleeping")
            sleep(12)
        
        del api_instance
        if not success:
            result['failed'] = True

        return result
