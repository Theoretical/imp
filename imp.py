import codecs
import os
import sys
import time
import emoji
import threading
from config import DynamicConfigDict, DynamicConfigList
import tools, tools.jobs

__author__ = 'Zeta'

import discord
import traceback


internal_config = DynamicConfigDict(file="internal_config.json", default_config={
    "discord": {
        "email": "change_me",
        "password": "change_me"
    },
    "updater": {
        "fallbacks": True,
        "repo": "https://github.com/zetahunter/imp.git",
        "update_interval": 60
    }
})

if os.path.exists("internal_config.json"):
    internal_config.load()
else:
    internal_config.save()

class Imp(discord.Client):

    class Command(object):
        def __init__(self, **kwargs):
            self.trigger = kwargs.get('trigger')
            self.command = str()
            self.message = None
            self.args = str()
            self.imp = Imp()

        def can_remove(self):
            return True

        def can_run(self):
            return True

        def run(self):
            print("{} is not implemented".format(self.__name__))

        def say(self, string):
            if self.imp is not None and self.message is not None:
                self.imp.send_message(self.message.channel, string, mentions=True)

        def reply(self, string):
            if self.message is not None:
                self.say("{author}, {message}".format(
                    author=self.message.author.mention(),
                    message=string
                ))

    class EventHandler(object):
        def __init__(self, **kwargs):
            self.imp = Imp()
            self.events = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scheduler = tools.jobs.JobScheduler(self)
        self.scheduler.start()
        self.commands = {}
        self._events = {}
        self.macros = {
            "error_not_privileged": "Error! {user} is not privileged to run {command}."
        }
        self.default_config = {
            'name': "Imp",
            'context_trigger': "!",
            'remove_trigger': '#',
            'author': "Zeta",
            'version': "Impoid v0.2.0",
            'privileged': [
                94129005791281152 #Zeta
            ]
        }
        self.ignored = DynamicConfigList(file="ignored.json", default_config=[])
        self.ignored.load()
        self.config = DynamicConfigDict(file="config.json", default_config=self.default_config)
        self.config.load()

        self.config.bind_to(self.internal_on_config_change)

        for event in self.events:
            self.events[event] = self.internal_event_handler(event)
            self._events[event] = []

        self._events['on_message'].append(self.internal_on_message)
        self._events['on_ready'].append(self.internal_on_ready)
        self._events['on_error'].append(self.internal_on_error)

    def is_privileged(self, id):
        return int(id) in self.config['privileged']

    def is_ignored(self, obj):
        if isinstance(obj, discord.Server):
            return "server_{}".format(obj.id) in self.ignored._config
        elif isinstance(obj, discord.Channel):
            return "channel_{}".format(obj.id) in self.ignored._config
        elif isinstance(obj, discord.User):
            return "user_{}".format(obj.id) in self.ignored._config
        return False

    def execute_command(self, command, **kwargs):
        if isinstance(command, Imp.Command):
            cmd = command
            cmd.command = str(command.__name__).lower()
        else:
            cmd = self.commands[command]
            cmd.command = command
        cmd.args = kwargs.get('args', None)
        cmd.message = kwargs.get('message', None)
        cmd.remove_triggered = kwargs.get('remove_triggered', None)
        if cmd.can_run():
            cmd.run()
            if cmd.remove_triggered and cmd.can_remove():
                self.delete_message(cmd.message)
        else:
            self.send_message(cmd.message.channel, self.macros['error_not_privileged'].format(
                user=cmd.message.author.mention(),
                command=command), mentions=True)

    def register_event_handler(self, event_handler):
        if isinstance(event_handler, Imp.EventHandler):
            for event in event_handler.events:
                self._events[event].append(event_handler.events[event])

    def register_command(self, command, trigger=None):
        if isinstance(command, Imp.Command):
            command.imp = self
            trigger = trigger or command.trigger

            if trigger is None:
                trigger = str(command.__name__).lower()

            if trigger not in self.commands:
                self.commands[trigger] = command

    def get_member(self, id):
        if id is None:
            return None
        for server in self.servers:
            for member in server.members:
                if member.id == id:
                    return member

    def _get__server(self, server_name):
        if server_name is None:
            return None
        for server in self.servers:
            if (isinstance(server_name, int) and server.id == server_name) \
                or (isinstance(server_name, str) and server_name.lower().strip() in str(server.name).lower().strip()):
                return server
        return None

    def _get_channel(self, server_name, channel_name):
        if server_name is None or channel_name is None:
            return None
        server = server_name if isinstance(server_name, discord.Server) else self._get__server(server_name)
        for channel in server.channels:
            if (isinstance(channel_name, int) and channel.id == channel_name) \
                or (isinstance(channel_name, str) and channel_name.lower().strip() in str(channel.name).lower().strip()):
                return channel
        return None

    def _get_member(self, server_name, member_name):
        if server_name is None or member_name is None:
            return None
        server = server_name if isinstance(server_name, discord.Server) else self._get__server(server_name)
        for member in server.members:
            if (isinstance(member_name, int) and member.id == member_name) \
                or (isinstance(member_name, str) and member_name.lower().strip() in str(member_name).lower().strip()):
                return member
        return None

    def _get_by_id(self, id):
        entity, ident = id.split("_", 1)
        if entity in "server":
            return self._get_server(ident)
        elif entity in "channel":
            return self.get_channel(ident)
        elif entity in "user":
            return self.get_member(ident)

    def internal_on_config_change(self, key, value):
        if key == "name":
            self.edit_profile(internal_config['discord']['password'], username=value)

    def _invoke_event(self, event_name, *args, **kwargs):
        try:
            for callback in self._events[event_name]:
                callback(*args, **kwargs)
        except Exception as e:
            for callback in self._events['on_error']:
                callback(event_name, *sys.exc_info())

    def internal_event_handler(self, event="", **kwargs):
        def event_handler(self, **kwargs):
            for callback in self._events[event or kwargs.get("event")]:
                callback(**kwargs)

        return event_handler

    def internal_on_ready(self):
        print('Imp is Connected!')
        print('Username: ' + self.user.id)
        print('ID: ' + self.user.id)

    def internal_on_error(self, event,typ, value, tb):
        self.error()

    def internal_on_message(self, message):
        msg = str(message.content)
        print("{server} | #{channel} - {user}: {message}".format(
            server=message.channel.server.name if isinstance(message.channel, discord.Channel) else 'Private Channel',
            channel=message.channel.name if isinstance(message.channel, discord.Channel) else message.channel.user.name,
            user=message.author,
            message=message.content.encode("utf-8")))

        if (self.is_ignored(message.channel) or self.is_ignored(message.author) or
            (isinstance(message.channel, discord.Channel) and self.is_ignored(message.channel.server))) \
                and not self.is_privileged(message.author.id):
            return

        if msg.startswith(self.config['context_trigger']):
            msg = msg.replace(self.config['context_trigger'], '', 1)
            remove_triggered = msg.startswith(self.config['remove_trigger'])
            msg = msg.replace(self.config['remove_trigger'], '', 1)
            if msg in self.commands:
                self.execute_command(msg,
                                     message=message,
                                     remove_triggered=remove_triggered)
            else:
                if ' ' in msg:
                    command, args = msg.split(' ', 1)
                    if command in self.commands:
                        self.execute_command(command,
                                             args=args,
                                             message=message,
                                             remove_triggered=remove_triggered)
        elif msg.startswith(self.config['remove_trigger']):
            try:
                delay_amount = int(''.join(x for x in msg.split(' ', 1)[0] if x.isdigit()))
            except:
                delay_amount = 5
            def _delete(self, message):
                self.delete_message(message)
            timer = threading.Timer(delay_amount, _delete, [self, message])
            timer.start()

    def say(self, channel, string):
        self.send_message(channel, string, mentions=True)

    def reply(self, message, string):
        self.say(message.channel, "{author}, {message}".format(
            author=message.author,
            message=string))

    def error(self, channel_respond=False):
        try:
            trace = traceback.format_exc()
            traceback.print_exc()
            try:
                lines = list(reversed(trace.splitlines()))
                report = [lines[0].strip()]
                for line in lines:
                    line = line.strip()
                    if line.startswith('File "'):
                        report.append(line[0].lower() + line[1:])
                        break
                else:
                    report.append('source unknown')

                signature = '%s (%s)' % (report[0], report[1])
                if channel_respond:
                    self.say(channel_respond, "{error}: {msg}".format(error=report[0], msg=report[1]))

                with codecs.open('exceptions.log', 'a', encoding='utf-8') as logfile:
                    logfile.write('Signature: %s\n' % signature)
                    logfile.write(trace)
                    logfile.write(
                        '----------------------------------------\n\n'
                    )
            except Exception as e:
                print("Could not save full traceback!")
        except Exception as e:
            traceback.print_exc()