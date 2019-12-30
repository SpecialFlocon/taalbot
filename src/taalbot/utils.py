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
        'color': 0x3498db,
        'fields': [
            {
                'name': _("Which article?"),
                'value': """
                    `${prefix}${cmd} taal`
                    `${prefix}${cmd} brood`
                """,
                'inline': False,
            },
            {
                'name': _("Set or replace article"),
                'value': """
                    `${prefix}${cmd} jaar het`
                    `${prefix}${cmd} thee de`
                    `${prefix}${cmd} pad ${both_articles}`
                """,
                'inline': False,
            }
        ]
    },
    'vandale': {
        'title': _("Van Dale free online dictionary search"),
        'description': _("Use this command to get a link to a word entry in Van Dale free online dictionary."),
        'color': 0x3498db,
        'fields': [
            {
                'name': _("Usage"),
                'value': "`${prefix}${cmd} <word>`",
                'inline': False,
            },
            {
                'name': _("Example"),
                'value': "`${prefix}${cmd} geschiedenis`",
                'inline': False,
            }
        ]
    },
    'forvo': {
        'title': _("Word pronuncation samples on Forvo"),
        'description': _("Use this command to get a link to word pronuncation recordings on Forvo."),
        'color': 0x3498db,
        'fields': [
            {
                'name': _("Usage"),
                'value': "`${prefix}${cmd} <word>`",
                'inline': False,
            },
            {
                'name': _("Example"),
                'value': "`${prefix}${cmd} aansprakelijkheidswaardevaststellingsver`",
                'inline': False,
            }
        ]
    }
}
