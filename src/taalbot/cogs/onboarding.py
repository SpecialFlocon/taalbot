from collections import defaultdict
from copy import copy
from discord.ext import commands
from discord.utils import find, get

from .. import const, exceptions

import asyncio
import discord
import gettext
import logging
import traceback


logger = logging.getLogger('taalbot.cogs.onboarding')

nt = gettext.NullTranslations()
g = nt.gettext

class OnboardStep:
    """
    A class that represents a step in the onboarding process.
    Can be subclassed to override message to send and possible choices.
    """

    def __init__(self, bot, member, choices=dict(), instructions_text=None, role_assignation_text=None):
        self.bot = bot
        self.member = member
        self.choices = choices
        self.instructions_text = instructions_text
        self.role_assignation_text = role_assignation_text

    async def warn_missing_role(self, role_name):
        await self.member.send(_("""
Beep boop derp, looks like I'm trying to assign a role that doesn't exist.
Don't worry, it's not your fault, it's the server team's, and I've already blamed them.
One of them will probably re-initiate the process for you.
"""))
        raise exceptions.RoleDoesNotExist(name)

    async def run(self):
        choices_emojis = self.choices.keys()
        try:
            message = await self.member.send(g(self.instructions_text))
        except discord.Forbidden:
            raise exceptions.RestrictedDMPolicy(self.member)
            return

        reaction_coros = [message.add_reaction(e) for e in choices_emojis]
        await asyncio.gather(*reaction_coros)

        def user_reacted_to_message(reaction, user):
            # user: the user who reacted to the message, member: the user we sent the DM to
            return user == self.member and reaction.message.id == message.id and str(reaction.emoji) in choices_emojis

        reaction, user = await self.bot.wait_for('reaction_add', check=user_reacted_to_message, timeout=const.EVENT_WAIT_TIMEOUT)
        for e, r in self.choices.items():
            if str(reaction.emoji) == e:
                break

        # If there is a role to assign, assign it.
        if r is not None:
            role = get(self.member.guild.roles, name=r)
            if not role:
                self.warn_missing_role(r)
                return

            await self.member.add_roles(role)
            await self.member.send(g(self.role_assignation_text).format(role.name))

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
        try:
            message = await self.member.send(g(self.instructions_text))
        except discord.Forbidden:
            raise exceptions.RestrictedDMPolicy(self.member)
            return

        def user_replied_with_country_name(message):
            country_role_color = discord.Colour(const.COUNTRY_ROLE_COLOR)
            country_names = [r.name.lower() for r in self.member.guild.roles if r.colour == country_role_color]
            return message.author == self.member and (message.content == '⏩' or message.content.lower() in country_names)

        country_name_message = await self.bot.wait_for('message', check=user_replied_with_country_name, timeout=const.EVENT_WAIT_TIMEOUT)
        if country_name_message.content == '⏩':
            return

        logger.debug("Country name message content: {}".format(country_name_message.content))
        country_role = find(lambda r: r.name.lower() == country_name_message.content.lower(), self.member.guild.roles)
        await self.member.add_roles(country_role)
        await self.member.send(g(self.role_assignation_text).format(country_role.name))

class AdditionalRoles(OnboardStep):
    """
    On-boarding process, step 4, optional: additional roles.
    Let user know about additional and optional tags, and prompt him to add some.
    User can also say when he's done, with or without additional roles.
    """

    def __init__(self, bot, member):
        be_role = get(member.roles, name=const.ROLE_NAME_BE)
        choices = {'🇧🇪': const.ROLE_NAME_BN} if not be_role else dict()
        choices.update(copy(const.ONBOARDING_ADDITIONAL_ROLES_MANDATORY_CHOICES))
        super().__init__(bot, member, choices, const.ONBOARDING_ADDITIONAL_ROLES_INSTRUCTIONS, const.ONBOARDING_ADDITIONAL_ROLES_ASSIGNED_ROLE)

    async def run(self):
        choices_emojis = self.choices.keys()
        try:
            message = await self.member.send(g(self.instructions_text))
        except discord.Forbidden:
            raise exceptions.RestrictedDMPolicy(self.member)
            return

        reaction_coros = [message.add_reaction(e) for e in choices_emojis]
        await asyncio.gather(*reaction_coros)

        def user_reacted_to_message(reaction, user):
            return user == self.member and reaction.message.id == message.id and str(reaction.emoji) in choices_emojis

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=user_reacted_to_message, timeout=const.EVENT_WAIT_ADDITIONAL_ROLES_TIMEOUT)
            except asyncio.TimeoutError:
                logger.info("Last step of the onboarding process for user {} timed out, wrapping up anyway.".format(self.member))
                if self.bot.log_channel:
                    await self.bot.log_channel.send(_("Last step of the onboarding process for user {} timed out, wrapping up anyway.").format(self.member.mention))
                await self.member.send(g(const.EVENT_WAIT_ADDITIONAL_ROLES_TIMEOUT_MESSAGE))
                return

            if str(reaction.emoji) == '✅':
                return

            for e, r in self.choices.items():
                if str(reaction.emoji) == e:
                    break

            # If there is a role to assign, assign it.
            if r is not None:
                role = get(self.member.guild.roles, name=r)
                if not role:
                    self.warn_missing_role(self.member, r)

                await self.member.add_roles(role)
                await self.member.send(g(self.role_assignation_text).format(role.name))

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

        country_role_color = discord.Colour(const.COUNTRY_ROLE_COLOR)
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
        ]

        resettable_roles = [r for rn in resettable_role_names for r in self.member.guild.roles if r.name == rn and r in self.member.roles]
        resettable_roles.extend([r for r in self.member.guild.roles if r.colour == country_role_color and r in self.member.roles])
        await self.member.remove_roles(*resettable_roles)

    async def restricted_dm_greet_fallback(self):
        greet_channel = get(self.member.guild.channels, name=self.bot.config.get('greetChannel')) or self.member.guild.system_channel

        logger.error("Cannot send DMs to user {}, aborted auto onboarding.".format(self.member))
        if self.bot.log_channel:
            await self.bot.log_channel.send(_("{} doesn't allow DMs from server members, no auto onboarding for him/her.").format(self.member.mention))
        await greet_channel.send(const.GREET_NEW_MEMBER_RESTRICTED_DM_MESSAGE.format(self.member.mention))

    async def run(self):
        await self.reset_roles()

        [StepClass] = self.steps['root']
        while StepClass is not None:
            logger.debug("Onboarding user {}, current step class: {}".format(self.member, StepClass))
            current_step = StepClass(self.bot, self.member)
            try:
                await current_step.run()
            except exceptions.RestrictedDMPolicy:
                await self.restricted_dm_greet_fallback()
                return
            except asyncio.TimeoutError:
                logger.warning("Onboarding process for user {} timed out.".format(self.member))
                if self.bot.log_channel:
                    await self.bot.log_channel.send(_("Onboarding process for user {} timed out.").format(self.member.mention))
                await self.member.send(g(const.EVENT_WAIT_TIMEOUT_MESSAGE))
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

        logger.info("User {} is done with the onboarding process.".format(self.member))
        if self.bot.log_channel:
            await self.bot.log_channel.send(_("User {} is done with the onboarding process.").format(self.member.mention))
        await self.member.send(g(const.ONBOARDING_FINAL_NOTE_TEXT))

class Onboarding(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def greet(self, member):
        greet_channel = get(member.guild.channels, name=self.bot.config.get('greetChannel')) or member.guild.system_channel
        await greet_channel.send(const.GREET_NEW_MEMBER_MESSAGE.format(member.mention))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        logger.info("Onboarding for user {} started upon server join.".format(member))
        if self.bot.log_channel:
            await self.bot.log_channel.send(_("Onboarding for user {} started upon server join.").format(member.mention))
        await self.greet(member)
        await OnboardProcess(self.bot, member).run()

    @commands.command(hidden=True)
    @commands.has_permissions(manage_roles=True)
    async def onboard(self, ctx, *, member: discord.Member=None):
        member = member or ctx.author
        logger.info("Onboarding for user {} has been requested by {}.".format(member, ctx.author))
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

            logger.info("Onboarding command invoked by user {} with insufficient permissions".format(author.name))
            logger.debug("Permissions for user {}: {}".format(author.name, ctx.channel.permissions_for(author)))
        else:
            if ctx.bot.log_channel:
                await ctx.bot.log_channel.send(const.LOG_CHANNEL_MSG.format(error))
            logger.error(traceback.format_exception(type(error), error, error.__traceback__))

def setup(bot):
    bot.add_cog(Onboarding(bot))
