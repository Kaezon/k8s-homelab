import argparse
import logging
import os
from pathlib import Path
import sys
from time import sleep
import urllib3
from urllib3.util import Retry

from git import Repo
import gitea_api
from gitea_api.rest import ApiException

# Make urllib a little quieter
urllib3.disable_warnings()
logging.captureWarnings(True)


# Parse args
parser = argparse.ArgumentParser()
parser.add_argument("-u", "--user",
                    help="Gitea username",
                    required=True)
parser.add_argument("-p", "--password",
                    help="Gitea password",
                    required=True)
parser.add_argument("--host",
                    help="Gitea URL (e.g. https://my-gitea-host.net)",
                    required=True)
parser.add_argument("-r", "--repo",
                    help="Gitea repo name",
                    required=True)
args = parser.parse_args()


PROJECT_DIR = Path(os.path.dirname(__file__)).resolve().parent.parent
GIT_REMOTE_NAME = 'cluster'
GIT_REMOTE_URL = f'{args.host}/{args.user}/{args.repo}'

configuration = gitea_api.Configuration()
configuration.host = f'{args.host}/api/v1'
configuration.verify_ssl = False
configuration.username = args.user
configuration.password = args.password

api_instance = gitea_api.RepositoryApi(
    gitea_api.ApiClient(configuration))

# Need to apply a custom Retry object
api_instance.api_client.rest_client.pool_manager.connection_pool_kw[
    'retries'] = Retry(total=10, backoff_factor=10)

success = False

# Keep trying to create the repo until it succeeds or we hit max retries
for i in range(10):
    try:
        api_instance.create_current_user_repo(
            body=gitea_api.CreateRepoOption(name=args.repo))
        success = True
        break
    except ApiException as e:
        if e.reason == "Service Temporarily Unavailable":
            print("Waiting for Gitea to become available...")
        elif e.reason == "Conflict":
            success = True
            print("Got conflict")
            break
        else:
            print("Exception when calling "
                "RepositoryApi->create_current_user_repo: %s\n" % e)
    print("Sleeping")
    sleep(12)

# Have to delete the API object, otherwise the thread pool never closes
# and prevents the process from terminating.
del api_instance
if not success:
    sys.exit(1)

# Make sure remote exists in repo
localRepo = Repo(PROJECT_DIR)
if GIT_REMOTE_NAME not in localRepo.remotes:
    localRepo.create_remote(GIT_REMOTE_NAME, GIT_REMOTE_URL)
else:
    localRepo.remote(GIT_REMOTE_NAME).set_url(GIT_REMOTE_URL)

# Set the remote and push
remote = localRepo.remote(GIT_REMOTE_NAME)
remote.fetch()
localRepo.git.push('--set-upstream', remote, localRepo.active_branch)