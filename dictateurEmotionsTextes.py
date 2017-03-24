# -*- coding: utf-8 -*-
"""
Ce module contient les textes des écrans
"""
__author__ = "Jean-Marc Rousselle"

# pour i18n:
# 1)  décommenter les lignes ci-après,
# 2) entourer les expressions à traduire par _DE()
# 3) dans le projet créer les dossiers locale/fr_FR/LC_MESSAGES
# en remplaçant fr_FR par la langue souhaitée
# 4) créer le fichier dictateurEmotions.po: dans invite de commande, taper:
# xgettext fichierTextes.py -p locale/fr_FR/LC_MESSAGES -d dictateurEmotions
# 5) avec poedit, éditer le fichier dictateurEmotions.po qui a été créé

# import os
# from le2mConfig.le2mParametres import LE2M_DIRECTORY_PROGRAMMES
# try:
#     import gettext
#     localedir = os.path.join(
#         LE2M_DIRECTORY_PROGRAMMES, "dictateurEmotions", "locale"
#     )
#     _DE = gettext.translation("dictateurEmotions", localedir).ugettext
# except ImportError:
#     _DE = lambda s: s

from collections import namedtuple
from le2mUtile.le2mUtileTools import get_pluriel
import dictateurEmotionsParametres as parametres

TITLE_MSG = namedtuple("TITLE_MSG", "titre message")

ROLE_JOUEUR_A = u" Vous êtes le joueur A"
ROLE_JOUEUR_B = u" Vous êtes le joueur B"


# ECRAN DECISION ===============================================================
DECISION_titre = u"Decision"
DECISION_explication = u"Vous avez une dotation de {}. Vous pouvez envoyer la quantité que vous souhaitez au joueur B.".format(parametres.DOTATION)
DECISION_explication_assoc = u"Vous avez une dotation de {}. Vous pouvez envoyer la quantité que vous souhaitez à l'association choisie.".format(parametres.DOTATION)
DECISION_label = u"Decision label text"
DECISION_erreur = TITLE_MSG(
    u"Warning",
    u"Warning message"
)
DECISION_confirmation = TITLE_MSG(
    u"Confirmation",
    u"Confirmation message"
)


# ECRAN RECAPITULATIF ==========================================================
def get_recapitulatif(*args):
    txtA = u"Vous êtiez le joueur A, voila ce que vous avez envoyé au joueur B et votre gain"
    txtB = u"Vous êtiez le joueur B, le joueur A a décidé de vous envoyer"
    return txtA,  txtB


# TEXTE FINAL PARTIE ===========================================================
def get_texte_final(gain_ecus, gain_euros):
    txt = u"Vous avez gagné {gain_en_ecu}, soit {gain_en_euro}.".format(
        gain_en_ecu=get_pluriel(gain_ecus, u"ecu"),
        gain_en_euro=get_pluriel(gain_euros, u"euro")
    )
    return txt
