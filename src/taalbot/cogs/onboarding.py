from collections import defaultdict
from discord.ext import commands
from discord.utils import find, get

from .. import const, exceptions

import asyncio
import discord
import functools
import logging


class OnboardStep:
    """
    A class that represents a step in the onboarding process.
    Can be subclassed to override message to send and possible choices.
    """

    def __init__(self, bot, member, choices=[], instructions_text=None, role_assignation_text=None):
        self.bot = bot
        self.member = member
        self.choices = choices
        self.instructions_text = instructions_text
        self.role_assignation_text = role_assignation_text

    @staticmethod
    async def warn_missing_role(member, name):
        await member.send(_("""
Beep boop derp, looks like I'm trying to assign a role that doesn't exist.
Don't worry, it's not your fault, it's the server team's, and I've already blamed them.
One of them will probably re-initiate the process for you.
"""))
        raise exceptions.RoleDoesNotExist(name)

    async def run(self):
        choices_emojis = [c[0] for c in self.choices]
        message = await self.member.send(self.instructions_text)
        for e in choices_emojis:
            await message.add_reaction(e)

        def user_reacted_to_message(reaction, user):
            # user: the user who reacted to the message, member: the user we sent the DM to
            return user == self.member and reaction.message.id == message.id and str(reaction.emoji) in choices_emojis

        reaction, user = await self.bot.wait_for('reaction_add', check=user_reacted_to_message, timeout=const.EVENT_WAIT_TIMEOUT)
        for c in self.choices:
            if str(reaction.emoji) == c[0]:
                break

        # If there is a role to assign, assign it.
        if c[1] is not None:
            role = get(self.member.guild.roles, name=c[1])
            if not role:
                self.warn_missing_role(self.member, c[1])

            await self.member.add_roles(role)
            await self.member.send(self.role_assignation_text.format(role.name))

class Introduction(OnboardStep):
    """
    On-boarding process, step 0: introduction
    Give a (not-so-)short explanation about how the server works,
    and what the user needs to do.
    """

    def __init__(self, bot, member):
        super().__init__(bot, member, const.ONBOARDING_INTRO_CHOICES, const.ONBOARDING_INTRO_INSTRUCTIONS)

class NativeSpeaker(OnboardStep):
    """
    On-boarding process, step 1: native speaker?
    Ask the user if he's a native Dutch speaker or not.
    """

    def __init__(self, bot, member):
        super().__init__(bot, member, const.ONBOARDING_NATIVE_SPEAKER_CHOICES, const.ONBOARDING_NATIVE_SPEAKER_INSTRUCTIONS, const.ONBOARDING_NATIVE_SPEAKER_ASSIGNED_ROLE)

class NativeDialect(OnboardStep):
    """
    On-boarding process, step 2, native speaker branch: which Dutch dialect/variant?
    Ask user which "dialect" of Dutch he speaks.
    """

    def __init__(self, bot, member):
        super().__init__(bot, member, const.ONBOARDING_NATIVE_DIALECT_CHOICES, const.ONBOARDING_NATIVE_DIALECT_INSTRUCTIONS, const.ONBOARDING_NATIVE_DIALECT_ASSIGNED_ROLE)

class NonNativeLevel(OnboardStep):
    """
    On-boarding process, step 2, non-native speaker branch: which Dutch level?
    Ask user what his Dutch level is.
    """

    def __init__(self, bot, member):
        super().__init__(bot, member, const.ONBOARDING_NON_NATIVE_LEVEL_CHOICES, const.ONBOARDING_NON_NATIVE_LEVEL_INSTRUCTIONS, const.ONBOARDING_NON_NATIVE_LEVEL_ASSIGNED_ROLE)

class Country(OnboardStep):
    """
    On-boarding process, step 3, optional: which country?
    Ask user which country he lives in.
    """

    def __init__(self, bot, member):
        super().__init__(bot, member, instructions_text=const.ONBOARDING_COUNTRY_INSTRUCTIONS, role_assignation_text=const.ONBOARDING_COUNTRY_ASSIGNED_ROLE)

    async def run(self):
        message = await self.member.send(self.instructions_text)

        def user_replied(message):
            return message.author == self.member and (message.content == '⏩' or \
                find(lambda r: r.lower() == message.content.lower(), const.COUNTRIES))

        country_name_message = await self.bot.wait_for('message', check=user_replied, timeout=const.EVENT_WAIT_TIMEOUT)
        if country_name_message.content == '⏩':
            return

        country_role = get(self.member.guild.roles, name=country_name_message.content.lower().capitalize())
        await self.member.add_roles(country_role)
        await self.member.send(self.role_assignation_text.format(country_role.name))

class AdditionalRoles(OnboardStep):
    """
    On-boarding process, step 4, optional: additional roles.
    Let user know about additional and optional tags, and prompt him to add some.
    User can also say when he's done, with or without additional roles.
    """

    def __init__(self, bot, member):
        be_role = get(member.roles, name=const.ROLE_NAME_BE)
        choices = ([('🇧🇪', const.ROLE_NAME_BE)] if not be_role else []) + const.ONBOARDING_ADDITIONAL_ROLES_MANDATORY_CHOICES
        super().__init__(bot, member, choices, const.ONBOARDING_ADDITIONAL_ROLES_INSTRUCTIONS, const.ONBOARDING_ADDITIONAL_ROLES_ASSIGNED_ROLE)

    async def run(self):
        choices_emojis = [c[0] for c in self.choices]
        message = await self.member.send(self.instructions_text)
        for e in choices_emojis:
            await message.add_reaction(e)

        def user_reacted_to_message(reaction, user):
            return user == self.member and reaction.message.id == message.id and str(reaction.emoji) in choices_emojis

        while True:
            reaction, user = await self.bot.wait_for('reaction_add', check=user_reacted_to_message, timeout=const.EVENT_WAIT_TIMEOUT)
            if str(reaction.emoji) == '✅':
                return

            for c in self.choices:
                if str(reaction.emoji) == c[0]:
                    break

            # If there is a role to assign, assign it.
            if c[1] is not None:
                role = get(self.member.guild.roles, name=c[1])
                if not role:
                    self.warn_missing_role(self.member, c[1])

                await self.member.add_roles(role)
                await self.member.send(self.role_assignation_text.format(role.name))

class OnboardProcess:
    """
    A class which represents different steps of the onboarding process as a graph.
    """

    def __init__(self, bot, member):
        # Construct graph
        adjacency_list = [
            ('root', Introduction),
            (Introduction, NativeSpeaker),
            (NativeSpeaker, NativeDialect),
            (NativeSpeaker, NonNativeLevel),
            (NativeDialect, Country),
            (NonNativeLevel, Country),
            (Country, AdditionalRoles),
            (AdditionalRoles, None)
        ]
        steps_graph = defaultdict(list)
        for k, v in adjacency_list:
            steps_graph[k].append(v)

        self.bot = bot
        self.member = member
        self.steps = steps_graph

    async def reset_roles(self):
        """
        Reset all applicable roles prior to onboarding process.
        """

        resettable_role_names = [
            const.ROLE_NAME_NATIVE,
            const.ROLE_NAME_NL,
            const.ROLE_NAME_BE,
            const.ROLE_NAME_SA,
            const.ROLE_NAME_LEVEL_O,
            const.ROLE_NAME_LEVEL_A,
            const.ROLE_NAME_LEVEL_B,
            const.ROLE_NAME_LEVEL_C,
            const.ROLE_NAME_WVDD,
            const.ROLE_NAME_SESSIONS,
            const.ROLE_NAME_CORRECT_ME,
            const.ROLE_NAME_BN,
        ] + const.COUNTRIES

        resettable_roles = [r for rn in resettable_role_names for r in self.member.guild.roles if r.name == rn and r in self.member.roles]
        await self.member.remove_roles(*resettable_roles)

    async def greet(self):
        greet_channel = get(self.member.guild.channels, name=self.bot.config.get('greetChannel')) or self.member.guild.system_channel
        greet_msg = self.bot.config.get('greetMessage')
        logging.debug("Greet message template: {}".format(greet_msg))

        if greet_channel and greet_msg:
            logging.info("User {} is done with the onboarding process.".format(self.member))
            if self.bot.log_channel:
                await self.bot.log_channel.send(_("User {} is done with the onboarding process.").format(self.member.mention))
            await greet_channel.send(greet_msg.format(name=self.member.mention))

    async def run(self):
        await self.reset_roles()

        [StepClass] = self.steps['root']
        while StepClass is not None:
            logging.debug("Onboarding user {}, current step class: {}".format(self.member, StepClass))
            current_step = StepClass(self.bot, self.member)
            try:
                await current_step.run()
            except asyncio.TimeoutError:
                logging.info("Onboarding process for user {} timed out.".format(self.member))
                if self.bot.log_channel:
                    await self.bot.log_channel.send(_("Onboarding process for user {} timed out.").format(self.member.mention))
                await self.member.send(const.EVENT_WAIT_TIMEOUT_MESSAGE)
                return

            next_step_classes = self.steps[StepClass]
            # After the "native speaker?" step, there are two possible paths.
            # Check if user has Native role or not to determine which one to follow.
            if next_step_classes == [NativeDialect, NonNativeLevel]:
                if get(self.member.roles, name=const.ROLE_NAME_NATIVE):
                    StepClass = NativeDialect
                else:
                    StepClass = NonNativeLevel
            # Just get the name of the class that corresponds to next step
            else:
                [StepClass] = self.steps[StepClass]

        await self.member.send(const.ONBOARDING_FINAL_NOTE_TEXT)
        await self.greet()

class Onboarding(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        logging.info("Onboarding for user {} started upon server join.".format(member))
        if self.bot.log_channel:
            await self.bot.log_channel.send(_("Onboarding for user {} started upon server join.").format(member.mention))
        await OnboardProcess(self.bot, member).run()

    @commands.command(hidden=True)
    @commands.has_permissions(manage_roles=True)
    async def onboard(self, ctx, *, member: discord.Member=None):
        member = member or ctx.author
        logging.info("Onboarding for user {} has been requested by {}.".format(member, ctx.author))
        if ctx.bot.log_channel:
            await ctx.bot.log_channel.send(_("Started onboarding for user {}, as requested by {}.").format(member.mention, ctx.author.mention))
        await OnboardProcess(self.bot, member).run()

    @onboard.error
    async def onboard_error(self, ctx, error):
        author = ctx.message.author
        if isinstance(error, commands.MissingPermissions) or isinstance(error, commands.MissingAnyRole):
            await ctx.send(_("{}, you are not allowed to run this command. If you'd like to go through on-boarding process again, ask a team member to initiate it for you.").format(author.mention))
            if ctx.bot.log_channel:
                await ctx.bot.log_channel.send("""
User {} without sufficient permissions tried to start the on-boarding process by running:
```
{}
```
""".format(author.mention, ctx.message.content))

            logging.info("Onboarding command invoked by user {} with insufficient permissions".format(author.name))
            logging.debug("Permissions for user {}: {}".format(author.name, ctx.channel.permissions_for(author)))
        else:
            if ctx.bot.log_channel:
                await ctx.bot.log_channel.send(const.LOG_CHANNEL_MSG.format(error))
            logging.error(traceback.format_exception(type(error), error, error.__traceback__))

def setup(bot):
    bot.add_cog(Onboarding(bot))
