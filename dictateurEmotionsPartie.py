# -*- coding: utf-8 -*-

from twisted.internet import defer
import logging
import random
from datetime import datetime
from sqlalchemy import Column, Integer, Float, ForeignKey, String

from le2mConfig.le2mParametres import MONNAIE
from le2mServ.le2mServParties import Partie
from le2mUtile.le2mUtileTools import get_monnaie

import dictateurEmotionsParametres as parametres
import dictateurEmotionsTextes as textes


logger = logging.getLogger("le2m.{}".format(__name__))


class PartieDE(Partie):
    __tablename__ = "partie_dictateurEmotions"
    __mapper_args__ = {'polymorphic_identity': 'dictateurEmotions'}
    partie_id = Column(Integer, ForeignKey('parties.id'), primary_key=True)
    
    DE_traitement = Column(Integer)
    DE_role = Column(Integer)
    DE_groupe_joueur = Column(Integer)
    DE_place_joueur_dans_groupe = Column(Integer)
    DE_dotation = Column(Integer)
    DE_envoi = Column(Integer)
    DE_recu = Column(Integer)
    DE_decision = Column(Integer)
    DE_le_gain = Column(Integer)
    DE_decision_temps = Column(Integer)
    DE_gain_ecus = Column(Float)
    
    def __init__(self, main_serveur, joueur):
        super(PartieDE, self).__init__("dictateurEmotions", "DE")
        self._main_serveur = main_serveur
        self.joueur = joueur
        self._texte_recapitulatif = u""
        self._texte_final = u""
        self.DE_gain_ecus = 0
        self.DE_gain_euros = 0
        self._histo_vars = [
            "DE_le_gain",
            "DE_gain_ecus"
        ]
        self._histo = [
            [u"Décision", u"Gain"]
        ]

    @defer.inlineCallbacks
    def configurer(self, *args):
        """
        permet de configurer la partie (traitement ...)
        :param args:
        :return:
        """
        # ici mettre en place la configuration
        yield (self.remote.callRemote("configurer", *args))

    @defer.inlineCallbacks
    def nouvelle_periode(self, periode):
        """
        Informe le remote du numéro de cette période (0)
        Vide l'historique
        :param periode: ici normalement 0 puis one-shot
        :return:
        """
        del self._histo[1:]
        yield (
            self.remote.callRemote("nouvelle_periode", periode)
        )
        logger.info(u"Période {} -> Ok".format(periode))
    
    @defer.inlineCallbacks
    def afficher_ecran_role(self):
        """
        Affiche l'écran de décision sur le remote.
        Récupère la ou les décisions, le temps de décision et enregistre le tout
        dans la base.
        :param args:
        :param kwargs:
        :return:
        """
    
        # Si TYPE_DICT = 0 les 2 premiers joueurs des groupes sont des joueurs A
        # sinon ils sont tous des joueurs A
        if parametres.TYPE_DICT == 0:
            if self.DE_place_joueur_dans_groupe == 0 or self.DE_place_joueur_dans_groupe == 1:
                self.DE_role = parametres.JOUEUR_A
            else:
                self.DE_role = parametres.JOUEUR_B
        else:
            self.DE_role = parametres.JOUEUR_A
        le_role = self.DE_role    
        debut = datetime.now()
        self.DE_decision = \
            yield(
                self.remote.callRemote("afficher_ecran_role", le_role)
        )
        self.joueur.afficher_info("u{}".format(self.DE_role))
        self.joueur.remove_wait_mode()    
    
    @defer.inlineCallbacks
    def afficher_ecran_decision(self):
        """
        Affiche l'écran de décision sur le remote.
        Récupère la ou les décisions, le temps de décision et enregistre le tout
        dans la base.
        :param args:
        :param kwargs:
        :return:
        """
    
        # Si TYPE_DICT = 0 les 2 premiers joueurs des groupes sont des joueurs A
        # sinon ils sont tous des joueurs A
        if parametres.TYPE_DICT == 0:
            if self.DE_place_joueur_dans_groupe == 0 or self.DE_place_joueur_dans_groupe == 1:
                self.DE_role = parametres.JOUEUR_A
            else:
                self.DE_role = parametres.JOUEUR_B
        else:
            self.DE_role = parametres.JOUEUR_A
        self.DE_decision = 0
        debut = datetime.now()
        if self.DE_role == parametres.JOUEUR_A:
            self.DE_decision = \
                yield(
                    self.remote.callRemote("afficher_ecran_decision")
            )
            self.DE_decision_temps = (datetime.now() - debut).seconds
            self.joueur.afficher_info("u{}".format(self.DE_decision))
            self.joueur.remove_wait_mode()
        
    def calculer_gain_periode(self):
        """
        Calcul du gain de la période
        :return:
        """
        logger.debug(u"Calcul du gain de la période")
        self.DE_gain_ecus = 0
        if parametres.TYPE_DICT == 0:
            if self.DE_role == 0:
                self.DE_le_gain = self.DE_decision
                self.DE_gain_ecus = parametres.DOTATION - self.DE_decision
            else:
                self.DE_le_gain = self.DE_recu
                self.DE_gain_ecus = self.DE_recu
        else:
            self.DE_le_gain = self.DE_decision
            self.DE_gain_ecus = parametres.DOTATION - self.DE_decision
        logger.debug(u"Gain période: {}".format(
            self.joueur, self.DE_gain_ecus)
        )

    @defer.inlineCallbacks
    def afficher_ecran_recapitulatif(self, *args):
        """
        Création du texte du récapitulatif et de l'historique puis affichage
        sur le remote
        :param args:
        :return:
        """
        logger.debug(u"Affichage de l'ecran recapitulatif")
        txtA, txtB = textes.get_recapitulatif(*args)
        if self.DE_role == 0:
            le_texte_recapitulatif = txtA
        else:
            le_texte_recapitulatif = txtB
        self._histo.append([getattr(self, e) for e in self._histo_vars])
        yield(self.remote.callRemote(
            "afficher_ecran_recapitulatif", le_texte_recapitulatif,
            self._histo)
        )
        self.joueur.afficher_info("Ok")
        self.joueur.remove_wait_mode()
    
    def calculer_gain_partie(self):
        """
        Calcul du gain de la partie
        :return:
        """
        logger.debug(u"Calcul du gain de la partie")
        # gain partie
        self.DE_gain_euros = \
            float(self.DE_gain_ecus) * \
            float(parametres.TAUX_CONVERSION)

        # texte final
        self._texte_final = textes.get_texte_final(
            self.DE_gain_ecus,
            self.DE_gain_euros
        )

        logger.debug(u"Texte final {}: {}".format(
            self.joueur, self._texte_final)
        )
        logger.info('{}: gain ecus:{}, gain euros: {:.2f}'.format(
            self.joueur, self.DE_gain_ecus,
            self.DE_gain_euros)
        )

