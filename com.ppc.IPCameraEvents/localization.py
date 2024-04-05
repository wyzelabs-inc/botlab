'''
Created on April 3, 2024

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Destry Teeter
'''

# Add any code here to import and apply localization one time.

import gettext
import os
import properties


# Set some default language here to allow the system to initialize
localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
gettext.translation('messages', localedir, languages=[properties.get_property(None, "DEFAULT_LANGUAGE")]).install()

def initialize(botengine):
    """
    Override the default language with the user's selected language
    :param botengine: BotEngine environment
    :return:
    """
    lang = botengine.get_language()
    if lang is None:
        lang = properties.get_property(botengine, "DEFAULT_LANGUAGE")

    localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
    localefile = os.path.join(localedir, '{}/LC_MESSAGES/messages.mo'.format(lang))
    if os.path.exists(localefile):
        gettext.translation('messages', localedir, languages=[lang]).install()
    else:
        default_language = properties.get_property(botengine, "DEFAULT_LANGUAGE")
        gettext.translation('messages', localedir, languages=[default_language]).install()