#!/bin/bash

bin/i18ndude rebuild-pot --pot src/collective/futures/locales/collective.futures.pot --merge src/collective/futures/locales/manual.pot --create collective.futures src/collective/futures

bin/i18ndude sync --pot src/collective/futures/locales/collective.futures.pot src/collective/futures/locales/*/LC_MESSAGES/collective.futures.po
