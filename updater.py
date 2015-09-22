import os
import time

__author__ = 'Alex'

import github, dulwich.porcelain

class GithubUpdater:
    def __init__(self, token="", fallbacks=True, repo="", update_interval=60):
        self.fallbacks = fallbacks
        self.repo = repo
        self.update_interval = update_interval
        self.github = github.Github(token)
        self.github_repo = self.github.get_repo(self.repo)


    def run(self):
        no_updates = True
        while no_updates:

            time.sleep(self.update_interval)

