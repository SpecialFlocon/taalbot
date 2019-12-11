"""
This file contains values that will never change at runtime,
but might still be occasionally changed by hand.
"""

API_VERSION = 'v1'
TAALBOT_CMD_BLUEPRINT = {
    'dehet': {
        'title': "\"De\"-word or \"het\"-word?",
        'description': """
Which article does this noun need? You could try to guess, or you could ask me!
Unless the noun is in plural, in which case it's **always** \"de\".
""",
        'color': 3447003, # 0x3498db, blue
        'fields': [
            {
                'name': "Which article?",
                'value': """
                    `!dehet taal`
                    `!dehet brood`
                """,
                'inline': False,
            },
            {
                'name': "Set or replace article",
                'value': """
                    `!dehet jaar het`
                    `!dehet thee de`
                    `!dehet pad {}`
                """.format('both'),
                'inline': False,
            }
        ]
    }
}
