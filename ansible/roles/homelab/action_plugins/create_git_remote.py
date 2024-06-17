from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.action import ActionBase
from git import Repo


class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        result = super(ActionModule, self).run(tmp, task_vars)
        args = self._task.args

        project_dir = args.get('project_dir')
        remote_name = args.get('name')
        remote_url = args.get('url')
        push = args.get('push')

        # Make sure remote exists in repo
        localRepo = Repo(project_dir)
        if remote_name not in localRepo.remotes:
            localRepo.create_remote(remote_name, remote_url)
        else:
            localRepo.remote(remote_name).set_url(remote_url)

        remote = localRepo.remote(remote_name)
        remote.fetch()
        if push:
            try:
                localRepo.git.push('--set-upstream', remote, localRepo.active_branch)
            except Exception:
                result['msg'] = f"Failed to push to {remote_url}"
                result['failed'] = True
                return result

        result['msg'] = f"Remote {remote_name} added"
        result['changed'] = True

        return result