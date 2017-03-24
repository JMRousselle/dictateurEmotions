# -*- coding: utf-8 -*-

from twisted.internet import defer
from twisted.spread import pb
import logging
import random

from le2mClient.le2mClientGui.le2mClientGuiDialogs import GuiRecapitulatif

import dictateurEmotionsParametres as parametres
from dictateurEmotionsGui import GuiDecision
from dictateurEmotionsGui import GuiRole

logger = logging.getLogger("le2m.{}".format(__name__))


class RemoteDE(pb.Referenceable):
    """
    Class remote, celle qui est contactée par le client (sur le serveur)
    """
    def __init__(self, main_client):
        self._main_client = main_client
        self._main_client.ajouter_remote('dictateurEmotions', self)
        self._periode_courante = 0
        self._historique = []

    def remote_configurer(self, *args):
        """
        Appelé au démarrage de la partie, permet de configurer le remote
        par exemple: traitement, séquence ...
        :param args:
        :return:
        """
        pass

    def remote_nouvelle_periode(self, periode):
        """
        Appelé au début de chaque période.
        L'historique est "vidé" s'il s'agit de la première période de la partie
        Si c'est un jeu one-shot appeler cette méthode en mettant 0
        :param periode: le numéro de la période courante
        :return:
        """
        logger.info(u"Période {}".format(periode))
        self._periode_courante = periode
        if self._periode_courante == 1:
            del self._historique[:]

    def remote_afficher_ecran_role(self, le_role):
        """
        Affiche l'écran de décision
        :return: deferred
        """
        logger.info(u"Affichage de l'écran de décision")
        if self._main_client.simulation:
            return 
        else: 
            defered = defer.Deferred()
            ecran_role = GuiRole(
                defered,
                self._main_client.automatique,
                self._main_client.gestionnaire_graphique.ecran_attente,
                self._periode_courante, self._historique,  le_role)
            ecran_role.show()
            return defered

    def remote_afficher_ecran_decision(self):
        """
        Affiche l'écran de décision
        :return: deferred
        """
        logger.info(u"Affichage de l'écran de décision")
        if self._main_client.simulation:
            decision = \
                random.randrange(
                    parametres.DECISION_MIN,
                    parametres.DECISION_MAX + parametres.DECISION_STEP,
                    parametres.DECISION_STEP
                )
            logger.info(u"Renvoi: {}".format(decision))
            return decision
        else: 
            defered = defer.Deferred()
            ecran_decision = GuiDecision(
                defered,
                self._main_client.automatique,
                self._main_client.gestionnaire_graphique.ecran_attente,
                self._periode_courante, self._historique)
            ecran_decision.show()
            return defered

    def remote_afficher_ecran_recapitulatif(self, texte_recap, historique):
        """
        Affiche l'écran récapitulatif
        :param texte_recap: le texte affiché
        :param historique: l'historique de la partie
        :return: deferred
        """
        self._historique = historique
        if self._main_client.simulation:
            return 1
        else:
            defered = defer.Deferred()
            ecran_recap = GuiRecapitulatif(
                defered,
                self._main_client.automatique,
                self._main_client.gestionnaire_graphique.ecran_attente,
                self._periode_courante, self._historique, texte_recap)
            ecran_recap.show()
            return defered
