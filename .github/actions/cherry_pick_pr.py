# This script is designed to create a cherry pick PR on every commit to master
#
# It is currently invoked as part of a github workfow with the content of the github event passed in
#
# When invoked on the gib runner, it has the following environment variables available
#
# To test locally:
# pip3 install PyGithub pygit2
# ARROW_GITHUB_API_TOKEN=<your token> python3 cherry_pick_pr.py <path_to_action>
#
import os
import sys

from github import Github

from pathlib import Path
p = Path(__file__)
repo_root = p.parent.parent

print("Using checkout in {}", repo_root);



if len(sys.argv) == 2:
    path_to_action = sys.argv[1]
else:
    print("USAGE: {} <path_to_github_action>")
    sys.exit(1)

token = os.environ.get('ARROW_GITHUB_API_TOKEN', None)
if token is None:
    print("GITHUB token must be supplied via ARROW_GITHUB_API_TOKEN environmet")
    sys.exit(1)


g = Github(token)

# Some relevant fields on the action:
# * `after` is the new commit,
# * `before` is the previous commit
#
# The plan here is to effectively create a new branch from active_release
# and cherry pick to there.
#

#https://www.pygit2.org/recipes/git-cherry-pick.html#cherry-picking-a-commit-without-a-working-copy
repo = pygit2.Repository('/path/to/repo')

cherry = repo.revparse_single('9e044d03c')
basket = repo.branches.get('basket')

base      = repo.merge_base(cherry.oid, basket.target)
base_tree = cherry.parents[0].tree

index = repo.merge_trees(base_tree, basket, cherry)
tree_id = index.write_tree(repo)

author    = cherry.author
committer = pygit2.Signature('Archimedes', 'archy@jpl-classics.org')

repo.create_commit(basket.name, author, committer, cherry.message,
                   tree_id, [basket.target])
