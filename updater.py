import os
import time
import pprint
# import gittle
import threading
import imp

class GitUpdater(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.fallbacks = imp.internal_config['updater']['fallbacks']
        self.repo = imp.internal_config['updater']['repo']
        self.update_interval = imp.internal_config['updater']['update_interval']
        self.local = os.path.dirname(os.path.realpath(__file__))
        # self.local_repo = porcelain.open_repo(self.repo)
        pprint.pprint(self.__dict__)

    def run(self):
        no_updates = True
        while no_updates:
            # pprint.pprint(porcelain.log(self.local_repo))
            # pprint.pprint(porcelain.ls_remote(str(self.repo).encode()))
            pprint.pprint("Stuff...")
            time.sleep(self.update_interval)

