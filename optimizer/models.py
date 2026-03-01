"""Modèles POO pour l'outil de répartition de production.

Contenu :
- Planet
- Batiment (Building)
- ChantierSpatial (hérite de Batiment)
- Vaisseau (base) + exemples de vaisseaux

Utilise `dataclasses` (stdlib) pour simplicité et immutabilité des attributs de base.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Optional

# Bonus global affectant le temps de construction du chantier spatial
BONUS_FDV_CHANTIER_SPATIAL :float = 0.0

@dataclass
class Batiment:
    """Représente un bâtiment générique sur une planète.

    - `name` : identifiant du type de bâtiment (ex: 'ChantierSpatial').
    - `level` : niveau courant sur la planète.
    - `global_props` : propriétés globales partagées entre toutes les instances de ce type
      (ex: coût par niveau, facteurs de vitesse). Peut être servi par la classe projet.
    """
    name: str
    level: int = 0
    global_props: Dict = field(default_factory=dict)

    def effective_factor(self) -> float:
        """Retourne un facteur multiplicatif générique dépendant du niveau.
        Méthode simple par défaut ; peut être surchargée.
        """
        return 1.0 + 0.1 * self.level


@dataclass
class ChantierSpatial(Batiment):
    """Bâtiment spécifique responsable de la construction des vaisseaux.

    On garde la logique simple : le temps de construction d'un vaisseau dépend
    du niveau du chantier (et d'un bonus global), via la méthode `build_time`.
    
    formule de base : 2^(niveau-1)
    cumulé :(coûts niveau 1) * - (1 - 2^niveau)
    """
    base_metal :int = 400
    base_cristal :int = 200
    base_deuterium :int = 100

    @property
    def build_time(self) -> float:
        """Retourne le temps de construction basé sur le niveau du batiment
        Formule (Métal + Cristal) / (2'500 * MAX (4 - niveau / 2, 1) * (1 + (niveau Usine de robots)) * (2 ^ (niveau Usine de Nanites)))
        """
        next_metal, next_cristal, _ = self.cost_at_level(self.level)
        temps = (next_metal + next_cristal) / (2_500 * max(4 - self.level / 2, 1))
        return temps
    
    def cost_at_level(self, level) -> int:
        next_metal = self.base_metal * 2 ** (self.level - 1) 
        next_cristal = self.base_metal * 2 ** (self.level - 1) 
        next_deutérium = self.base_metal * 2 ** (self.level - 1) 
        return next_metal, next_cristal, next_deutérium

@dataclass
class Planet:
    """Représente une planète.

    - `name` : nom
    - `coords` : (galaxy, system, position)
    - `is_main` : bool indiquant si c'est la planète principale
    - `buildings` : liste d'instances de `Batiment` présents sur la planète
    """
    name: str
    coords: Tuple[int, int, int]
    is_main: bool = False
    buildings: List[Batiment] = field(default_factory=list)

    def get_building(self, building_name: str) -> Optional[Batiment]:
        for b in self.buildings:
            if b.name == building_name:
                return b
        return None

    def add_or_update_building(self, building: Batiment) -> None:
        existing = self.get_building(building.name)
        if existing:
            existing.level = building.level
            existing.global_props = building.global_props
        else:
            self.buildings.append(building)


@dataclass
class Vaisseau:
    """Classe de base pour un vaisseau.

    - `type_name` : identifiant du vaisseau (ex: 'Chasseur').
    - `base_build_time` : temps de construction de référence (en secondes ou minutes).
    - `params` : autres paramètres (coût, capacité, etc.)
    - `ready` : quantité déjà disponible sur la planète (optionnel)
    """
    type_name: str
    base_build_time: float
    params: Dict = field(default_factory=dict)
    ready: int = 0

    def build_time_on(self, chantier: ChantierSpatial, other_buildings: List[Batiment]=None) -> float:
        """Calcule le temps de construction sur une planète donnée en fonction du
        niveau du `chantier` et d'autres bâtiments éventuels.

        Formule proposée (simple et homogène pour tous les vaisseaux) :
            time = base_build_time * chantier.build_time_multiplier() / building_factor
        where `building_factor` is product of effective_factor() of relevant buildings (>=1).

        Cette formule est volontairement simple ; tu pourras la remplacer ultérieurement.
        """
        other_buildings = other_buildings or []
        building_factor = 1.0
        for b in other_buildings:
            building_factor *= b.effective_factor()
        return float(self.base_build_time) * chantier.build_time_multiplier() / max(1.0, building_factor)


# Exemples de sous-classes de vaisseaux (peuvent servir pour typage spécifique)
class ChasseurLeger(Vaisseau):
    def __init__(self, ready: int = 0):
        super().__init__(type_name='Chasseur Léger', 
                         base_build_time=30.0, 
                         params={'attack': 50}, 
                         ready=ready)


class GrandTransporteur(Vaisseau):
    def __init__(self, ready: int = 0):
        super().__init__(type_name='Grand Transporteur', 
                         base_build_time=120.0, 
                         params={'capacity': 1000}, 
                         ready=ready)


# Utilitaire : liste fixe des types de vaisseaux disponibles (instances prototypes)
DEFAULT_VAISSEAUX = [
    ChasseurLeger(),
    GrandTransporteur(),
    # ajouter d'autres prototypes ici (jusqu'à ~10)
]
