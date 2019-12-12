# taalbot

A Discord bot that interacts with the HTTP API provided by [taalapi](https://github.com/ThePib/taalapi)

### Quickstart

```
TODO
```

### Translations

This project uses GNU gettext and its Python implementation for i18n and l10n.
Current translations are in the [locales](locales) directory.

The template file is [here](taalbot.pot). It can be used to contribute additional translations.
For the translation to be picked up, a `.mo` file is needed:

```console
cd <repo>
mkdir -p locales/<language>/LC_MESSAGES
xgettext --from-code="UTF-8" --keyword=_ --language=Python --package-name=taalbot --package-version=x.y.z -o taalbot.pot src/taalbot/*.py src/taalbot/cogs/*.py
msginit --input=taalbot.pot --locale=<language> --output=locales/<language>/LC_MESSAGES/taalbot.po
msgfmt --output-file=locales/<language>/LC_MESSAGES/taalbot.mo locales/<language>/LC_MESSAGES/taalbot.po
```

To update existing `.po` files:

```console
cd <repo>
xgettext --from-code="UTF-8" --keyword=_ --language=Python --package-name=taalbot --package-version=x.y.z -o taalbot.pot src/taalbot/*.py src/taalbot/cogs/*.py
msgmerge --update locales/<language>/LC_MESSAGES/taalbot.po taalbot.pot
msgfmt --output-file=locales/<language>/LC_MESSAGES/taalbot.mo locales/<language>/LC_MESSAGES/taalbot.po
```

All PRs are welcome!
