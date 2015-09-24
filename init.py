#!/usr/bin/env python3
from importlib import reload

import commands
import imp
import updater
import multiprocessing as mp
import time

client = None
master_child = None

def restart(delay=0):
    global master_child
    if master_child is not None:
        master_child.terminate()
    reload(updater)
    reload(imp)
    reload(commands)
    master_child = mp.Process(target=start)
    time.sleep(delay)
    master_child.start()
    master_child.join()

def start():
    global client
    if client is not None:
        client.logout()
        del client

    client = imp.Imp()
    client.login(imp.internal_config['discord']['email'], imp.internal_config['discord']['password'])
    client.register_command(commands.Countdown(), 'countdown')
    client.register_command(commands.IsUp(), 'isup')
    client.register_command(commands.PyEval(), 'py')
    client.register_command(commands.Wolfram(), 'wa')
    client.register_command(commands.Calc(), 'calc')
    client.register_command(commands.Reload(), 'reload')
    client.register_command(commands.Me(), "me")
    client.register_command(commands.Ignore(), "ignore")
    client.register_command(commands.Roll(), "roll")
    client.register_command(commands.Everyone(), "everyone")
    client.register_command(commands.Whois(), "whois")
    client.register_command(commands.Ping(), "ping")
    client.register_command(commands.Save(), "save")
    client.register_command(commands.Load(), "load")
    client.register_command(commands.Help(), "help")
    client.register_command(commands.Kill(), "kill")
    client.register_command(commands.Info(), "info")
    client.register_command(commands.Set(), "set")
    client.register_command(commands.Get(), "get")
    client.register_command(commands.Echo(), "echo")
    client.register_command(commands.Awesome(), "awesome")

    updater_thread = updater.GitUpdater()
    updater_thread.start()
    client.run()


if __name__ == "__main__":
    restart()
