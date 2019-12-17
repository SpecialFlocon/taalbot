"""
This file contains values that will never change at runtime,
but might still be occasionally changed by hand.
"""

API_REQUEST_TIMEOUT = 3 # seconds
API_VERSION = 'v1'

EVENT_WAIT_TIMEOUT = 600 # seconds
EVENT_WAIT_TIMEOUT_MESSAGE = _("""
You took so long to answer, I gave up waiting and interrupted the process.
Your profile is still incomplete, ask a team member in one of the server channels to re-kick the process for you:
`@Admin`, `@Moderator`, `@Mentor`, `@Developer`
""")

LOG_CHANNEL_MSG = """
**Error report**
```
{}
```
"""

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
