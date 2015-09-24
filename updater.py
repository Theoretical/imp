import os
import time
import threading
import multiprocessing as mp

from git import Repo, RemoteProgress
import imp
import init


class MyProgressPrinter(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        print(op_code, cur_count, max_count, cur_count / (max_count or 100.0), message or "NO MESSAGE")

class GitUpdater(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.fallbacks = imp.internal_config['updater']['fallbacks']
        self.repo = imp.internal_config['updater']['repo']
        self.update_interval = imp.internal_config['updater']['update_interval']
        self.local = os.path.dirname(os.path.realpath(__file__))
        self.local_repo = Repo(self.local)

    def run(self):
        no_updates = True
        imp.internal_version = "Git Build #{short_sha}".format(short_sha=self.local_repo.commit().hexsha[:7])
        print(imp.internal_version)
        while no_updates:
            for remote in self.local_repo.remotes:
                local_commit = self.local_repo.commit()
                info = remote.fetch()
                remote_commit = info[0].commit
                remote_name = info[0].name
                if remote_name != self.repo:  # Pick repo from settings.
                    continue
                if remote_commit == local_commit :  # If an update.
                    continue
                if self.fallbacks:
                    self.local_repo.git.execute("git checkout -B fallback")
                    self.local_repo.git.execute("git checkout master")
                data = self.local_repo.git.execute("git pull {} {}".format(*self.repo.split('/')))
                print(data)
                print("We have updated to #{}".format(self.local_repo.commit().hexsha[:7]))
                print("Will undergo a cold reload now.")
                init.restart(1)
                no_updates = False
            time.sleep(self.update_interval)

