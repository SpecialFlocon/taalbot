"""
This file contains miscellaneous data that are freely available
across the rest of the codebase.
"""

TAALBOT_CMD_BLUEPRINT = {
    'dehet': {
        'title': _("\"De\"-word or \"het\"-word?"),
        'description': _("""
Which article does this noun need? You could try to guess, or you could ask me!
Unless the noun is in plural, in which case it's **always** \"de\"."""),
        'color': 3447003, # 0x3498db, blue
        'fields': [
            {
                'name': _("Which article?"),
                'value': """
                    `!dehet taal`
                    `!dehet brood`
                """,
                'inline': False,
            },
            {
                'name': _("Set or replace article"),
                'value': """
                    `!dehet jaar het`
                    `!dehet thee de`
                    `!dehet pad {}`
                """.format(_('both')),
                'inline': False,
            }
        ]
    }
}
