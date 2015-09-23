import html
import re
from socket import timeout
import random
import pprint
import multiprocessing as mp
import datetime
import discord
import imp

import tools
import tools.calculator
import tools.web
import tools.jobs
import init
from imp import Imp

__author__ = 'Alex'

BASE_TUMBOLIA_URI = 'https://tumbolia-two.appspot.com/'

class Help(Imp.Command):
    def run(self):
        """
        Sends this help text in private message to you.
        """
        msg = ""
        for command in self.imp.commands:
            msg += "{name} - {desc}\n".format(
                name=command,
                desc=tools.trim_docstring(self.imp.commands[command].run.__doc__))

        self.imp.send_message(self.message.author,
                              "Hey, here are some of my commands:\n{commands}".format(
                                  commands=msg
                              ))

class Info(Imp.Command):
    def run(self):
        """
        Sends general information on server and the bot to channel.
        """
        self.imp.send_message(self.message.channel,
            "I am {name}, my version is {version} and I was created by {author}.\n"
            "We are on '{server_name}' server created by '{server_owner}' located in '{server_region}' region.\n"
            "Talking in #{channel_name}, there are {user_online_count} users online and {user_idle_count} users idle out of total {user_count}.".format(
                name=self.imp.config['name'],
                version="<{} / {}>".format(self.imp.config['version'], imp.internal_version),
                author=self.imp.config['author'],
                server_name=self.message.channel.server.name if isinstance(self.message.channel, discord.Channel) else "Private Channel",
                server_owner=self.message.channel.server.owner.name if isinstance(self.message.channel, discord.Channel) else "Nobody",
                server_region=self.message.channel.server.region if isinstance(self.message.channel, discord.Channel) else "Nowhere",
                channel_name=self.message.channel.name,
                user_count=len(self.message.channel.server.members) if isinstance(self.message.channel, discord.Channel) else 0,
                user_online_count=sum('online' in user.status for user in self.message.channel.server.members) if isinstance(self.message.channel, discord.Channel) else 0,
                user_idle_count=sum('idle' in user.status for user in self.message.channel.server.members) if isinstance(self.message.channel, discord.Channel) else 0
            ))


class Set(Imp.Command):
    def can_run(self):
        return self.imp.is_privileged(self.message.author.id)

    def run(self):
        key, value = str(self.args).split(' ', 1)
        old = self.imp.config[key] or None
        self.imp.config[key] = value
        self.imp.send_message(self.message.channel,
                              "{who} changed '{key}' from '{fromvalue}' to '{tovalue}'.".format(
                                  who=self.message.author.mention(),
                                  key=key,
                                  fromvalue=old,
                                  tovalue=value
                                  ), mentions=True)


class Get(Imp.Command):
    def run(self):
        self.imp.send_message(self.message.channel, "{victim}, {key} is {value}.".format(
            victim=self.message.author.mention(),
            key=self.args,
            value=self.imp.config[self.args]), mentions=True)


class Echo(Imp.Command):
    def can_run(self):
        return self.imp.is_privileged(self.message.author.id)

    def run(self):
        """
        Sends argument as message to channel.
        """
        self.imp.send_message(self.message.channel, self.args, mentions=True)


class Awesome(Imp.Command):
    def run(self):
        """
        Sends "... is awesome!" to channel, @ mentions and normal text works, if no argument - author is used.
        """
        if len(self.message.mentions) > 0:
            msg = ""
            for user in self.message.mentions:
                if user == self.message.mentions[0]:
                    msg = "{}".format(user.mention())
                elif user == self.message.mentions[-1]:
                    msg = "{} and {}".format(msg, user.mention())
                else:
                    msg = "{}, {}".format(msg, user.mention())
            if len(self.message.mentions) > 1:
                msg += " are awesome!"
            else:
                msg = "{} is awesome!".format(msg)
        elif self.args != None:
            msg = "{} is/are awesome!".format(self.args)
        else:
            msg = "{} is awesome!".format(self.message.author.mention())
        self.imp.send_message(self.message.channel, msg, mentions=True)


#By SolarPolarMan.
class Kill(Imp.Command):
    def run(self):
        """
        Sends message ".a. killed .v. in the ... using ...!" to channel where a is author and v is @ mention or text.
        """
        rooms = ["Hall", "Lounge", "Dining Room", "Kitchen", "Ballroom",
                 "Conservatory", "Billard Room", "Library", "Study"]
        wep = ["a Candlestick", "a Wrench", "some Rope",
               "a Revolver", "a Knife", "a Lead Pipe"]
        self.imp.send_message(
            self.message.channel,
            "{who} killed {victim} in the {room} using {weapon}!".format(
                who=self.message.author.mention(),
                victim= self.message.mentions[0].mention() if len(self.message.mentions) > 0 else "himself" if self.args is None else self.args,
                room=random.choice(rooms),
                weapon=random.choice(wep)), mentions=True)


class Save(Imp.Command):
    def can_run(self):
        return self.imp.is_privileged(self.message.author.id)

    def run(self):
        self.imp.config.save()
        self.imp.send_message(self.message.channel, "{user}, I've saved configuration file.".format(
            user=self.message.author.mention()
        ), mentions=True)

class Load(Imp.Command):
    def can_run(self):
        return self.imp.is_privileged(self.message.author.id)

    def run(self):
        self.imp.config.load()
        self.imp.send_message(self.message.channel, "{user}, I've loaded configuration file.".format(
            user=self.message.author.mention()
        ), mentions=True)


class Ping(Imp.Command):
    def run(self):
        """
        Sends ".a., Pong!" to channel.
        """
        self.imp.send_message(self.message.channel, "{user}, Pong!".format(
            user=self.message.author.mention()), mentions=True)


class Whois(Imp.Command):
    def run(self):
        """
        Sends general whois info on @ mentioned users (multiple supported)
        """
        msg = "{}, \n".format(self.message.author.mention())
        for mention in self.message.mentions:
            real_target = self.imp.get_member(mention.id)
            msg += "{victim} has joined at {joined_at}, " \
                   "currently {mute} mute, {deaf} deaf, {playing} and is {status}.\n".format(
                author=self.message.author.mention(),
                victim=real_target.mention(),
                joined_at=real_target.joined_at,
                mute="is" if real_target.mute else "not",
                deaf="is" if real_target.deaf else "not",
                playing="is playing {}".format(real_target.game_id) if real_target.game_id else "not playing",
                status=real_target.status)
        self.imp.send_message(self.message.channel, msg, mentions=True)



class Everyone(Imp.Command):
    def can_run(self):
        return self.imp.is_privileged(self.message.author.id)

    def run(self):
        """
        Sends a broadcast to everyone online or idle in channel, privileged users only.
        """
        msg = ""
        for user in self.message.channel.server.members:
            if "online" in user.status or "idle" in user.status:
                if user is self.message.channel.server.members[0]:
                    msg = "Attention! {}".format(user.mention())
                elif user is self.message.channel.server.members[-1]:
                    msg += " and {}".format(user.mention())
                else:
                    msg += ", {}".format(user.mention())
        msg += ": {}".format(self.args)
        self.imp.send_message(self.message.channel, msg, mentions=True)


class Roll(Imp.Command):
    def run(self):
        """
        Sends a message of dice roll based on (dices)d(sides) where dices is dice count and sides is side count.
        """
        dice_info = self.args.split('d')
        pprint.pprint(dice_info)
        result = 0
        if int(dice_info[0]) > 100000 or int(dice_info[1]) > 100000:
            return
        for dice in range(0, int(dice_info[0])):
            result += random.randint(1, int(dice_info[1]))
        self.imp.send_message(self.message.channel, "{user}, you rolled {dice} and got {result}.".format(
            user=self.message.author.mention(),
            dice=self.args,
            result=result
        ), mentions=True)


class Me(Imp.Command):
    def run(self):
        """
        Sends a message in form of ".a. *.m.*" where a is author and m is args.
        """
        self.imp.send_message(self.message.channel, "{user} *{message}*".format(
            user=self.message.author.mention(),
            message=self.args
        ), mentions=True)

class Ignore(Imp.Command):
    def can_run(self):
        return self.imp.is_privileged(self.message.author.id)

    def run(self):
        """
        Ignore management utility, privileged users only.
        """
        parser = tools.ArgumentParser(prog='Ignore', add_help=False, imp=self.imp, imp_message=self.message)
        parser.add_argument('action', choices=['add', 'remove', 'list', 'save', 'load'])
        parser.add_argument('target', choices=['server', 'channel', 'user'], nargs="?")
        parser.add_argument('name', action="store", nargs="?")

        if self.args is None:
            return self.reply("For fuck sake, give me some arguments okay.")
        args = parser.parse_args(self.args.split())

        if args.action in ['add', 'remove']:
            if args.action in 'add':
                if args.target in 'server':
                    server = self.imp._get__server(args.name)
                    print(server)
                    if server is not None:
                        self.imp.ignored.append("server_{}".format(server.id))
                if args.target in 'channel':
                    channel = self.imp._get_channel(self.message.channel.server, args.name)
                    if channel is not None:
                        self.imp.ignored.append("channel_{}".format(channel.id))
                if args.target in 'user':
                    if len(self.message.mentions) > 0:
                        user = self.message.mentions[0]
                    else:
                        user = self.imp._get_member(self.message.channel.server, args.name)
                    if user is not None:
                        self.imp.ignored.append("user_{}".format(user.id))
            if args.action in 'remove':
                if args.target in 'server':
                    server = self.imp._get__server(args.name)
                    if server is not None:
                        self.imp.ignored.remove("server_{}".format(server.id))
                if args.target in 'channel':
                    channel = self.imp._get_channel(self.message.channel.server, args.name)
                    if channel is not None:
                        self.imp.ignored.remove("channel_{}".format(channel.id))
                if args.target in 'user':
                    if len(self.message.mentions) > 0:
                        user = self.message.mentions[0]
                    else:
                        user = self.imp._get_member(self.message.channel.server, args.name)
                    if user is not None:
                        self.imp.ignored.remove("user_{}".format(user.id))
            self.imp.send_message(self.message.channel,
                                  "{author}, I will {args.action} ignore for {args.target} '{args.name}'".format(
                                      author=self.message.author.mention(),
                                      args=args
                                  ), mentions=True)
        elif args.action in ['list']:
            ignores = "".join("{} - {},\n".format(
                ignore,
                self.imp._get_by_id(ignore).name) for ignore in self.imp.ignored)
            self.imp.send_message(self.message.channel,
                                  "{author}, these are the following ignores:\n{ignores}".format(
                                      author=self.message.author.mention(),
                                      ignores=ignores
                                  ), mentions=True)
        elif args.action in ['save']:
            self.imp.ignored.save()
            self.imp.send_message(self.message.channel,
                                  "{author}, I've saved ignore list.".format(
                                      author=self.message.author.mention()), mentions=True)
        elif args.action in ['load']:
            self.imp.ignored.load()
            self.imp.send_message(self.message.channel,
                                  "{author}, I've loaded ignore list.".format(
                                      author=self.message.author.mention()), mentions=True)


class Reload(Imp.Command):
    def can_run(self):
        return self.imp.is_privileged(self.message.author.id)

    def run(self):
        """
        Reload management utility, privileged users only.
        """
        self.imp.send_message(self.message.channel,
            "{author}, I will now begin cold reboot, please wait 1 second.".format(
                author=self.message.author.mention()
            ), mentions=True)
        init.restart(1)
        p = mp.current_process()
        try:
            p.terminate()
        except:
            pass


class Calc(Imp.Command):
    def run(self):
        """
        Sends a result based on mathematical query.
        """
        eqn = self.args.replace(',', '.')
        try:
            result = tools.calculator.eval_equation(eqn)
            result = "Equation: {} Result:{:.10g}".format(eqn, result)
        except ZeroDivisionError:
            result = "Division by zero is not supported in this universe."
        except Exception as e:
            result = "{error}: {msg}".format(error=type(e).__name__, msg=e)
        self.imp.send_message(self.message.channel, result)

class Wolfram(Imp.Command):
    def run(self):
        """
        Sends response from Wolfram Alpha calculator
        """
        query = self.args
        uri = BASE_TUMBOLIA_URI + 'wa/'
        answer = str()
        try:
            answer = tools.web.get(uri + tools.web.quote(query.replace('+', 'plus')), 45)
        except timeout as e:
            return self.reply('[WOLFRAM ERROR] Request timed out')
        except Exception:
            self.imp.error(channel_respond=self.message.channel)
        if answer:
            answer = html.unescape(answer)
            match = re.search('\\\:([0-9A-Fa-f]{4})', answer)
            if match is not None:
                char_code = match.group(1)
                char = chr(int(char_code, 16))
                answer = answer.replace('\:' + char_code, char).strip()
            waOutputArray = answer.split(";")
            if(len(waOutputArray) < 2):
                if(answer.strip() == "Couldn't grab results from json stringified precioussss."):
                    # Answer isn't given in an IRC-able format, just link to it.
                    self.say('[WOLFRAM]Couldn\'t display answer, try http://www.wolframalpha.com/input/?i=' + query.replace(' ', '+'))
                else:
                    self.say('[WOLFRAM ERROR]' + answer)
            else:

                self.reply("Wolfram has returned with your answers!\n Request: '{0}', Response: \n{1}".format(
                    waOutputArray.pop(0),
                    "".join ("'{}' =>\n".format(item.strip()) if item is not waOutputArray[-1] else "Finally '{}'.".format(item.strip())  for item in waOutputArray),
                ))
                pprint.pprint(waOutputArray)
            waOutputArray = []
        else:
            self.reply('Sorry, no result.')


class PyEval(Imp.Command):
    def run(self):
        """
        Sends a response of evaluated python expression.
        """
        if self.args is None:
            return

        uri = BASE_TUMBOLIA_URI + "py/"
        answer = tools.web.get(uri + tools.web.quote(self.args))
        if answer:
            self.reply(answer)
        else:
            self.reply('Sorry, no result.')

class IsUp(Imp.Command):
    def run(self):
        """
        Sends a response of whatever website is up.
        """
        if self.args is None:
            return self.reply("How about you give me a website for starters? ...")

        try:
            response = tools.web.get(self.args)
        except Exception:
            return self.reply("{} looks down from here...".format(self.args))

        if response:
            return self.reply("{} looks fine to me.".format(self.args))
        else:
            return self.reply("{} looks down from here...".format(self.args))

class Countdown(Imp.Command):
    def run(self):
        """
        Sends a response with countdown to <year> <month> <day>
        """
        return self.reply("Not now.")
        # if self.args is None:
        #     return self.reply("Please use proper format: 2012 12 21")
        # text = self.args.split()
        # if text and (text[0].isdigit() and text[1].isdigit() and text[2].isdigit() and len(text) == 3):
        #     then = datetime.datetime(int(text[0]), int(text[1]), int(text[2]))
        #     diff = (then - datetime.datetime.now(tz=datetime.utc))
        #     return self.reply("{days} days, {hours} hours and {minutes} minutes until {text[0]} {text[1]} {text[2]}.".format(
        #         days=int(diff.days),
        #         hours=int(diff.seconds / 60 / 60),
        #         minutes=int(diff.seconds / 60 - int(diff.seconds / 60 / 60) * 60),
        #         text=text
        #     ))
        # else:
        #     return self.reply("Please use proper format: 2012 12 21")

class Invite(Imp.Command):
    def can_run(self):
        return self.imp.is_privileged(self.message.author.id)

    def run(self):
        if self.args is None:
            return self.reply("Please, give me a command okay.")
        command = self.args.split()
