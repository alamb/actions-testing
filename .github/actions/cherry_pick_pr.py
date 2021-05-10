# This script is designed to create a cherry pick PR on every commit to master
#
# Usage: python3 cherry_pick_pr.py <path_to_event_json>
#
# It is currently invoked as part of a github workfow with the content of the github event passed in
#
# AKA the value of
# GITHUB_EVENT_PATH=/home/runner/work/_temp/_github_workflow/event.json
#
# When invoked on the gib runner, it has the following environment variables available
#
# To test locally:
# pip3 install PyGithub
# ARROW_GITHUB_API_TOKEN=<your token> python3 cherry_pick_pr.py example_webhooks/commit_to_master.json
#
import os
import sys
import json
import six
import subprocess

from github import Github
from pathlib import Path



TARGET_BRANCH='active_release'

p = Path(__file__)
repo_root = p.parent.parent

## TEMP
#repo_root = '/tmp/actions-testing';
print("Using checkout in {}".format(repo_root));



# Get the action's body into action
if len(sys.argv) == 2:
    path_to_action = sys.argv[1]
    with open(path_to_action) as f:
        action = json.loads(f.read())
else:
    print("USAGE: {} <path_to_event_jsob>")
    sys.exit(1)

token = os.environ.get('ARROW_GITHUB_API_TOKEN', None)
if token is None:
    print("GITHUB token must be supplied via ARROW_GITHUB_API_TOKEN environmet")
    sys.exit(1)

g = Github(token)
repo = g.get_repo('alamb/actions-testing')

# from merge_pr.py from arrow repo
def run_cmd(cmd):
    if isinstance(cmd, six.string_types):
        cmd = cmd.split(' ')

    try:
        output = subprocess.check_output(cmd)
    except subprocess.CalledProcessError as e:
        # this avoids hiding the stdout / stderr of failed processes
        print('Command failed: %s' % cmd)
        print('With output:')
        print('--------------')
        print(e.output)
        print('--------------')
        raise e

    if isinstance(output, six.binary_type):
        output = output.decode('utf-8')
    return output


os.chdir(repo_root)


# Some relevant fields on the action:
# * `after` is the new commit,
# * `before` is the previous commit
new_sha = action['after']
new_sha_short = run_cmd("git rev-parse --short {}".format(new_sha)).strip()
new_branch = 'cherry_pick_{}'.format(new_sha_short)

run_cmd(['git', 'config', 'user.email', 'dev@arrow.apache.com']
run_cmd(['git', 'config', 'user.name', 'Arrow-RS Automation']

print("Creating cherry pick from {} to {}".format(new_sha_short, new_branch))
run_cmd(['git', 'fetch', 'origin', 'active_release'])
run_cmd(['git', 'checkout', 'active_release'])
run_cmd(['git', 'checkout', '-b', new_branch])
run_cmd(['git', 'cherry-pick', new_sha])
run_cmd(['git', 'push', '-u', 'origin'])


commit = repo.get_commit(new_sha)
for orig_pull in commit.get_pulls():
    print ('Commit was in original pull {}', pr.html_url)


new_title = 'Cherry pick {}'.format(new_sha)
new_commit_message = 'Automatic cherry-pick of {}\n'.format(new_sha);
for orig_pull in commit.get_pulls():
    new_commit_message += '* Originally appeared in {}: {}\n'.format(orig_pull.html_url, orig_pull.title)
    new_title = 'Cherry pick {}'.format(orig_pull.title)


#
# The plan here is to effectively create a new branch from active_release
# and cherry pick to there.
#


pr = repo.create_pull(title=new_title,
                      body=new_commit_message,
                      base='refs/heads/active_release',
                      head='refs/heads/{}'.format(new_branch),
                      maintainer_can_modify=True
                 )
print('Created PR {}'.format(pr.html_url))
