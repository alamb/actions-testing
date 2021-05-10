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
# pip3 install PyGithub pygit2
# ARROW_GITHUB_API_TOKEN=<your token> python3 cherry_pick_pr.py example_webhooks/commit_to_master.json
#
import os
import sys
import pygit2
import json

from github import Github
from pathlib import Path

TARGET_BRANCH='active_release'

p = Path(__file__)
repo_root = p.parent.parent

## TEMP
repo_root = '/tmp/actions-testing';
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

# Some relevant fields on the action:
# * `after` is the new commit,
# * `before` is the previous commit
new_sha = action['after']

#
# The plan here is to effectively create a new branch from active_release
# and cherry pick to there.
#

#https://www.pygit2.org/recipes/git-cherry-pick.html#cherry-picking-a-commit-without-a-working-copy
repo = pygit2.Repository(repo_root)

for remote in repo.remotes:
    print("Remote is {} @ {}".format(remote.name, remote.url))

cherry = repo.revparse_single(new_sha)
if cherry is None:
    print('Can not find revision {}'.format(new_shar))
    sys.exit(1)

basket = repo.branches.get(TARGET_BRANCH)
if basket is None:
    print('Can not find target branch {}'.format(TARGET_BRANCH))
    sys.exit(1)

print('Creating PR into active_release for commit {} into {}'.format(cherry.short_id, basket.name))


base      = repo.merge_base(cherry.oid, basket.target)
base_tree = cherry.parents[0].tree

index = repo.merge_trees(base_tree, basket, cherry)
tree_id = index.write_tree(repo)

author    = cherry.author
committer = pygit2.Signature('Archimedes', 'archy@jpl-classics.org')



new_branch_name = "cherry_pick_{}".format(cherry.short_id)
new_branch = repo.branches.local.create(new_branch_name, repo.get(basket.target))
print('Created new branch {}'.format(new_branch.name))

commit_message = 'Automatically created via cherry-pick from {}\n{}'.format(cherry.id, cherry.message);

new_commit = repo.create_commit(new_branch.name, author, committer, commit_message,
                   tree_id, [new_branch.target])

print("made new merge commit: ", new_commit);

print("Pushing to remote");
repo.remotes['origin'].push([new_branch.name])




g = Github(token)
