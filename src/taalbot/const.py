"""
This file contains values that will never change at runtime,
but might still be occasionally changed by hand.
"""

def _(m): return m

API_REQUEST_TIMEOUT = 3 # seconds
API_VERSION = 'v1'

COUNTRY_ROLE_COLOR = 0xa5b3bd

EVENT_WAIT_TIMEOUT = 600 # seconds
EVENT_WAIT_TIMEOUT_MESSAGE = _("""
You took so long to answer, I gave up waiting and interrupted the process.
Your profile is still incomplete. A team member can re-initiate the process for you.
""")
EVENT_WAIT_ADDITIONAL_ROLES_TIMEOUT = 120 # seconds
EVENT_WAIT_ADDITIONAL_ROLES_TIMEOUT_MESSAGE = _("I haven't seen any activity for a while, so I'm going to assume you are done with additional roles!")

GREET_NEW_MEMBER_DM_BACKOFF = 3 # seconds
GREET_NEW_MEMBER_MESSAGE = "Hallo {}, welkom op **Nederlands Leren**! I'll send you a DM to help you get the right roles."
GREET_NEW_MEMBER_RESTRICTED_DM_MESSAGE = "Couldn't send you a DM ➡️ please read {} and assign yourself the appropriate roles in {}!"

LOG_CHANNEL_MSG = """
**Error report**
```
{}
```
"""

ROLE_NAME_STAFF = "Staff"
ROLE_NAME_NATIVE = "Native"
ROLE_NAME_NL = "NL"
ROLE_NAME_BE = "BE"
ROLE_NAME_SA = "SA"
ROLE_NAME_LEVEL_O = "Niveau O"
ROLE_NAME_LEVEL_A = "Niveau A"
ROLE_NAME_LEVEL_B = "Niveau B"
ROLE_NAME_LEVEL_C = "Niveau C"
ROLE_NAME_WVDD = "Woord"
ROLE_NAME_SESSIONS = "Sessies"
ROLE_NAME_CORRECT_ME = "Verbeter mij"
ROLE_NAME_BN = "BN"

ONBOARDING_INTRO_CHOICES = {'▶️': None}
ONBOARDING_INTRO_INSTRUCTIONS = _("""
Hello, and welcome to **Nederlands Leren**! Let me introduce myself: I am taalbot, a bot that does things. I primarily live on this server.
I would like to walk you through our introduction process, so that you can experience the server to its fullest in no time!

For now, you only have access to a few channels, but there are many more!
In order for you to get the most out of your journey on this server, we first need to assign yourself some roles.
They will automatically give you access to currently hidden channels, and also let fellow members know about your Dutch proficiency level, so that they can adapt themselves!

Shall we get started? React to this message with ▶️, like I just did! This will be our main interaction method during the process.
""")

ONBOARDING_NATIVE_SPEAKER_ASSIGNED_ROLE = _("Nice, I've assigned you the **{}** role!")
ONBOARDING_NATIVE_SPEAKER_CHOICES = {'👍': ROLE_NAME_NATIVE, '👎': None}
ONBOARDING_NATIVE_SPEAKER_INSTRUCTIONS = _("""
Right, first things first, let's talk about your proficiency.
Are you a **native Dutch speaker**?
""")

ONBOARDING_NATIVE_DIALECT_ASSIGNED_ROLE = _("Okay. I've assigned you the **{}** role.")
ONBOARDING_NATIVE_DIALECT_CHOICES = {'🇳🇱': ROLE_NAME_NL, '🇧🇪': ROLE_NAME_BE, '🇸🇷': ROLE_NAME_SA}
ONBOARDING_NATIVE_DIALECT_INSTRUCTIONS = _("""
OK! Which Dutch do you speak?

🇳🇱 The Netherlands
🇧🇪 Belgium (Flanders)
🇸🇷 Suriname, Sint-Maarten, Sint-Eustatius, Saba + ABC Islands
""")

ONBOARDING_NON_NATIVE_LEVEL_ASSIGNED_ROLE = _("Okay. I've assigned you the **{}** role.")
ONBOARDING_NON_NATIVE_LEVEL_CHOICES = {'🇴': ROLE_NAME_LEVEL_O, '🇦': ROLE_NAME_LEVEL_A, '🇧': ROLE_NAME_LEVEL_B, '🇨': ROLE_NAME_LEVEL_C}
ONBOARDING_NON_NATIVE_LEVEL_INSTRUCTIONS = _("""
OK! What is your current Dutch level?
Are you unsure, or need more info? Check https://en.wikipedia.org/wiki/Common_European_Framework_of_Reference_for_Languages#Common_reference_levels.

🇴: **Onbekend** (unknown), total beginner
🇦: **Basic user**, corresponds to CEFR A1 (breakthrough) and A2 (waystage)
🇧: **Independent user**, corresponds to CEFR B1 (threshold) and B2 (vantage)
🇨: **Proficient user**, corresponds to CEFR C1 (advanced) and C2 (mastery)
""")

ONBOARDING_COUNTRY_ASSIGNED_ROLE = _("🌍 Great! I added the **{}** role to your profile!")
ONBOARDING_COUNTRY_INSTRUCTIONS = _("""
We're making progress! Now, if you want, you can tell me the name of the **country you live in**.

I said earlier that we'd communicate via reactions, but there are far too many different options!
For this time only, I am asking you to *type* the country name (in Dutch!)
Send ⏩ to skip this step.

Example: **Nederland**

If you don't know what yours is, here is a list of country names in Dutch:
https://www.101languages.net/dutch/country-names-dutch/
""")

ONBOARDING_ADDITIONAL_ROLES_ASSIGNED_ROLE = _("👍 Gave you the **{}** role!")
ONBOARDING_ADDITIONAL_ROLES_MANDATORY_CHOICES = {'📗': ROLE_NAME_WVDD, '🏫': ROLE_NAME_SESSIONS, '💪': ROLE_NAME_CORRECT_ME, '✅': None}
ONBOARDING_ADDITIONAL_ROLES_INSTRUCTIONS = _("""
Awesome, you're *almost* set! 🥳
There are still a few optional roles you can decide to add to your profile.
*Note*: these roles can also be obtained later, should you ever change your mind.

🇧🇪 **BN**: if you are interested in Belgian Dutch! Gives access to the #belgië channel. You won't see this option if you obtained `BE` or `België` role earlier, as people with those roles are automatically given access.
📗 **Woord**: get a notification when a new *woord van de dag* (word of the day) is posted in #woord-vd-dag.
🏫 **Sessies**: get a notification when members of this server organize impromptu / planned (voice) Dutch sessions.
💪 **Verbeter mij**: this tag lets natives (or everyone) know that you'd like your mistakes to be corrected.
✅ When you're satisfied with your choices.
""")

ONBOARDING_FINAL_NOTE_TEXT = _("""
Phew, finally done!
Take a look at <#238393894969147392>, as I believe people there just gave you, or will give you, a warm welcome! (Let me know if they don't, though!)
Make sure to read the rules in <#238393736478851074>, too!
Veel plezier!
""")

FORVO_SEARCH_BASE_URL = "https://forvo.com/search"
VANDALE_SEARCH_BASE_URL = "https://www.vandale.nl/gratis-woordenboek/nederlands/betekenis"
