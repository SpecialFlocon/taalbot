from discord.ext import commands
from discord.utils import find, get

from .. import const, exceptions

import asyncio
import discord
import logging


# TODO(thepib): this monstrosity of a class is stack overflow bound, at the very least.
# Make it less of a horror-show!
class OnboardProcess:
    """
    A class which methods represent a step of the onboarding process.
    Used to temporarily keep track of user choices.
    """

    def __init__(self, bot):
        self.bot = bot

    async def warn_missing_role(self, member, name):
        await member.send(_("""
Beep boop derp, looks like I'm trying to assign a role that doesn't exist.
Don't worry, it's not your fault, it's the server team's, and I've already blamed them.
One of them will probably re-initiate the process for you.
"""))
        raise exceptions.RoleDoesNotExist(name)

    async def reset_roles(self, member):
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
        ]

        resettable_roles = [r for rn in resettable_role_names for r in member.guild.roles if r.name == rn and r in member.roles]
        await member.remove_roles(*resettable_roles)

    async def introduction(self, member):
        """
        On-boarding process, step 0: introduction
        Give a (not-so-)short explanation about how the server works,
        and what the user needs to do.
        """

        # Reset all applicable roles of the member
        await self.reset_roles(member)

        text = _("""
Hello, and welcome to **Nederlands Leren**! Let me introduce myself: I am taalbot, a bot that does things. I primarily live on this server.
I would like to walk you through our introduction process, so that you can experience the server to its fullest in no time!

For now, you only have access to a few channels, but there are many more!
In order for you to get the most out of your journey on this server, we first need to assign yourself some roles.
They will automatically give you access to currently hidden channels, and also let fellow members know about your Dutch proficiency level, so that they can adapt themselves!

Shall we get started? React to this message with ▶️, like I just did! This will be our main interaction method during the process.
""")
        message = await member.send(text)
        await message.add_reaction('▶️')

        def user_reacted_to_message(reaction, user):
            # user: the user who reacted to the message, member: the user we sent the DM to
            return user == member and reaction.message.id == message.id and str(reaction.emoji) == '▶️'

        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=user_reacted_to_message, timeout=const.EVENT_WAIT_TIMEOUT)
        except asyncio.TimeoutError:
            logging.info("Onboarding process for user {} timed out.".format(member))
            return await member.send(const.EVENT_WAIT_TIMEOUT_MESSAGE)

        # Got a 👍, proceed to next step
        await self.native_speaker(member)

    async def native_speaker(self, member):
        """
        On-boarding process, step 1: native speaker?
        Ask the user if he's a native Dutch speaker or not.
        """

        choices = ['👍', '👎']
        text = _("""
Right, first things first, let's talk about your proficiency.
Are you a **native Dutch speaker**?
""")
        message = await member.send(text)
        for c in choices:
            await message.add_reaction(c)

        def user_reacted_to_message(reaction, user):
            return user == member and reaction.message.id == message.id and str(reaction.emoji) in choices

        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=user_reacted_to_message, timeout=const.EVENT_WAIT_TIMEOUT)
        except asyncio.TimeoutError:
            logging.info("Onboarding process for user {} timed out.".format(member))
            return await member.send(const.EVENT_WAIT_TIMEOUT_MESSAGE)

        if str(reaction.emoji) == '👍':
            native_role = get(member.guild.roles, name=const.ROLE_NAME_NATIVE)
            if not native_role:
                self.warn_missing_role(member, const.ROLE_NAME_NATIVE)

            await member.add_roles(native_role)
            await member.send(_("Nice, I've assigned you the **{}** role!").format(native_role.name))

            # Got a 👍, proceed to next step, native Dutch branch
            await self.native_which_dialect(member)
        else:
            # Got a 👎, proceed to next step, non-native Dutch branch
            await self.non_native_which_level(member)

    async def native_which_dialect(self, member):
        """
        On-boarding process, step 2, native speaker branch: which Dutch dialect/variant?
        Ask user which "dialect" of Dutch he speaks.
        """

        choices = ['🇳🇱', '🇧🇪', '🇸🇷']
        text = _("""
OK! Which Dutch do you speak?

🇳🇱 The Netherlands
🇧🇪 Belgium (Flanders)
🇸🇷 Suriname, Sint-Maarten, Sint-Eustatius, Saba + ABC Islands
""")
        message = await member.send(text)
        for c in choices:
            await message.add_reaction(c)

        def user_reacted_to_message(reaction, user):
            return user == member and reaction.message.id == message.id and str(reaction.emoji) in choices

        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=user_reacted_to_message, timeout=const.EVENT_WAIT_TIMEOUT)
        except asyncio.TimeoutError:
            logging.info("Onboarding process for user {} timed out.".format(member))
            return await member.send(const.EVENT_WAIT_TIMEOUT_MESSAGE)

        if str(reaction.emoji) == '🇳🇱':
            role_to_add = const.ROLE_NAME_NL
        elif str(reaction.emoji) == '🇧🇪':
            role_to_add = const.ROLE_NAME_BE
        else:
            role_to_add = const.ROLE_NAME_SA

        dutch_dialect_role = get(member.guild.roles, name=role_to_add)
        if not dutch_dialect_role:
            self.warn_missing_role(member, role_to_add)

        await member.add_roles(dutch_dialect_role)
        await member.send(_("Okay. I've assigned you the **{}** role.").format(dutch_dialect_role.name))

        await self.country(member)

    async def non_native_which_level(self, member):
        """
        On-boarding process, step 2, non-native speaker branch: which Dutch level?
        Ask user what his Dutch level is.
        """

        choices = ['🇴', '🇦', '🇧', '🇨']
        text = _("""
OK! What is your current Dutch level?
Are you unsure, or need more info? Check https://en.wikipedia.org/wiki/Common_European_Framework_of_Reference_for_Languages#Common_reference_levels.

🇴: **Onbekend** (unknown), total beginner
🇦: **Basic user**, corresponds to CEFR A1 (breakthrough) and A2 (waystage)
🇧: **Independent user**, corresponds to CEFR B1 (threshold) and B2 (vantage)
🇨: **Proficient user**, corresponds to CEFR C1 (advanced) and C2 (mastery)
""")
        message = await member.send(text)
        for c in choices:
            await message.add_reaction(c)

        def user_reacted_to_message(reaction, user):
            return user == member and reaction.message.id == message.id and str(reaction.emoji) in choices

        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=user_reacted_to_message, timeout=const.EVENT_WAIT_TIMEOUT)
        except asyncio.TimeoutError:
            logging.info("Onboarding process for user {} timed out.".format(member))
            return await member.send(const.EVENT_WAIT_TIMEOUT_MESSAGE)

        if str(reaction.emoji) == '🇴':
            role_to_add = const.ROLE_NAME_LEVEL_O
        elif str(reaction.emoji) == '🇦':
            role_to_add = const.ROLE_NAME_LEVEL_A
        elif str(reaction.emoji) == '🇧':
            role_to_add = const.ROLE_NAME_LEVEL_B
        else:
            role_to_add = const.ROLE_NAME_LEVEL_C

        dutch_level_role = get(member.guild.roles, name=role_to_add)
        if not dutch_level_role:
            self.warn_missing_role(member, role_to_add)

        await member.add_roles(dutch_level_role)
        await member.send(_("Okay. I've assigned you the **{}** role.").format(dutch_level_role.name))

        await self.country(member)

    async def country(self, member):
        """
        On-boarding process, step 3: which country?
        Ask user which country he lives in.
        """

        text = _("""
We're making progress! Now, if you want, you can tell me the name of the **country you live in**.

I said earlier that we'd communicate via reactions, but there are far too many different options!
For this time only, I am asking you to *type* the country name (in Dutch!)
Send ⏩ to skip this step.

Example: **Nederland**

If you don't know what yours is, here is a list of country names in Dutch:
https://www.101languages.net/dutch/country-names-dutch/
""")
        message = await member.send(text)

        def user_replied(message):
            return message.author == member and (message.content == '⏩' or \
                find(lambda r: r.name.lower() == message.content.lower(), member.guild.roles))

        try:
            country_name_message = await self.bot.wait_for('message', check=user_replied, timeout=const.EVENT_WAIT_TIMEOUT)
        except asyncio.TimeoutError:
            logging.info("Onboarding process for user {} timed out.".format(member))
            return await member.send(const.EVENT_WAIT_TIMEOUT_MESSAGE)

        if country_name_message.content == '⏩':
            return await self.additional_roles(member)

        country_role = get(member.guild.roles, name=country_name_message.content.lower().capitalize())
        await member.add_roles(country_role)
        await member.send(_("🌍 Great! I added the **{}** role to your profile!").format(country_role.name))

        await self.additional_roles(member)

    async def additional_roles(self, member):
        """
        On-boarding process, step 4, optional: additional roles
        Let user know about additional and optional tags are there, and prompt him
        """

        be_role = get(member.roles, name=const.ROLE_NAME_BE)
        choices = (['🇧🇪'] if not be_role else []) + ['📗', '🏫', '💪', '✅']
        text = _("""
Awesome, you're *almost* set! 🥳
There are still a few optional roles you can decide to add to your profile.

🇧🇪 **BN**: if you are interested in Belgian Dutch! Gives access to the #belgië channel. You won't see this option if you obtained `BE` or `België` role earlier, as people with those roles are automatically given access.
📗 **Woord**: get a notification when a new *woord van de dag* (word of the day) is posted in #woord-vd-dag.
🏫 **Sessies**: get a notification when members of this server organize impromptu / planned (voice) Dutch sessions.
💪 **Verbeter mij**: this tag lets natives (or everyone) know that you'd like your mistakes to be corrected.

You can "subscribe" to any of those roles, or just click ✅ if none of them interest you, or when you are done.
""")
        message = await member.send(text)
        for c in choices:
            await message.add_reaction(c)

        def user_reacted_to_message(reaction, user):
            return user == member and reaction.message.id == message.id and str(reaction.emoji) in choices

        # TODO(thepib): creating multiple asyncio loops might be a performance nightmare?
        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=user_reacted_to_message, timeout=const.EVENT_WAIT_TIMEOUT)
            except asyncio.TimeoutError:
                logging.info("Onboarding process for user {} timed out.".format(member))
                return await member.send(const.EVENT_WAIT_TIMEOUT_MESSAGE)

            if str(reaction.emoji) == '✅':
                return await self.final_note(member)

            if str(reaction.emoji) == '🇧🇪':
                role_to_add = const.ROLE_NAME_BN
            elif str(reaction.emoji) == '📗':
                role_to_add = const.ROLE_NAME_WVDD
            elif str(reaction.emoji) == '🏫':
                role_to_add = const.ROLE_NAME_SESSIONS
            else:
                role_to_add = const.ROLE_NAME_CORRECT_ME

            role = get(member.guild.roles, name=role_to_add)
            if not role:
                self.warn_missing_role(member, role_to_add)

            await member.add_roles(role)
            await member.send(_("👍 Gave you the **{}** role!").format(role.name))

        await self.final_note(member)

    async def final_note(self, member):
        """
        On-boarding process end
        Give user a final note, and send a welcome message in the system channel!
        """

        text = _("""
Phew, finally done!
Take a look at #nederlands-leren, as I believe people there just gave you, or will give you, a warm welcome! (Let me know if they don't, though!)
Make sure to read the rules in #informatie, too!
Veel plezier!
""")
        await member.send(text)
        await self.greet(member)

    async def greet(self, member):
        greet_channel = get(member.guild.channels, name=self.bot.config.get('greetChannel')) or member.guild.system_channel
        greet_msg = self.bot.config.get('greetMessage')
        logging.debug("Greet message template: {}".format(greet_msg))

        if greet_channel and greet_msg:
            await greet_channel.send(greet_msg.format(name=member.mention))

class Onboarding(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.process = OnboardProcess(bot)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.process.introduction(member)

    @commands.command(hidden=True)
    @commands.has_permissions(manage_roles=True)
    async def onboard(self, ctx, *, member: discord.Member=None):
        member = member or ctx.author
        logging.info("Onboarding for user {} has been requested by {}.".format(member, ctx.author))
        await ctx.bot.log_channel.send(_("Started onboarding for user {}, as requested by {}").format(member, ctx.author))
        await self.process.introduction(member)

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
