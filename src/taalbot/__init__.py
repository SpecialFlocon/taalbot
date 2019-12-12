import gettext


try:
    t = gettext.translation('taalbot', 'locales')
except FileNotFoundError as e:
    # Capture exceptions to report the error the way we want to.
    # TODO(thepib): using print() is a transient solution. Implement proper logging.
    print("Failed to load translations: {}".format(e))
    t = gettext.NullTranslations()
finally:
    t.install()
