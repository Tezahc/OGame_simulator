"""Modèles POO (refacto) pour l'outil de répartition.

- `Planet.batiments` est un container d'attributs (chantier_spatial, usine_robot, usine_nanites),
  chaque instance est unique et liée à la planète (b.planet = planet).
- `Batiment.build_time(level)` calcule la formule de base puis, si l'instance
  est attachée à une planète, applique les modificateurs issus d'autres bâtiments.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, List, Dict, Optional
from abc import ABC, abstractmethod


@dataclass(frozen=True)
class Cost:
    metal: int
    cristal: int
    deuterium: int

    def as_dict(self) -> Dict[str, int]:
        return {"metal": self.metal, "cristal": self.cristal, "deuterium": self.deuterium}


@dataclass
class Batiment(ABC):
    """Bâtiment générique.

    - Les sous-classes DOIVENT définir la propriété `base_cost` qui renvoie un `Cost`
      (coût du passage au niveau 1).
    - `growth` est le facteur multiplicatif par niveau (par défaut 2.0).

    `build_time` est défini par défaut ici à partir des coûts ;
    """

    name: str
    level: int = 0
    growth: float = 2.0

    @property
    @abstractmethod
    def base_cost(self) -> Cost:
        raise NotImplementedError

    def cost_at_level(self, level: int) -> Cost:
        lvl = max(1, level)
        exp = lvl - 1
        return Cost(
            metal=int(self._resource_cost(self.base_cost.metal, exp)),
            cristal=int(self._resource_cost(self.base_cost.cristal, exp)),
            deuterium=int(self._resource_cost(self.base_cost.deuterium, exp)),
        )

    def _resource_cost(self, base: int, exponent: int) -> float:
        return base * (self.growth ** exponent)

    def build_time(self, level: int) -> float:
        """Temps de construction final pour ce bâtiment au `level` demandé.

        - calcule d'abord le temps de base (métal+cristal) / (2500 * max(4 - level/2, 1))
        - si l'instance est attachée à une planète (`self.planet`), applique les modificateurs
          des bâtiments pertinents (ici `usine_robot` et `usine_nanites`) selon :
              time = time_base / ((1 + lvl_usine_robot) * (2 ** lvl_usine_nanites))
        """
        costs = self.cost_at_level(level)
        time_base = (costs.metal + costs.cristal) / (2500 * max(4 - level / 2, 1))

        # appliquer modificateurs planétaires si l'instance est rattachée
        planet = getattr(self, 'planet', None)
        if planet is None:
            return time_base

        # récupérer niveaux des bâtiments auxiliaires (défaut 0 si absent)
        try:
            lvl_ur = planet.batiments.usine_robot.level
        except Exception:
            lvl_ur = 0
        try:
            lvl_un = planet.batiments.usine_nanites.level
        except Exception:
            lvl_un = 0

        modifier = (1 + lvl_ur) * (2 ** lvl_un)
        if modifier <= 0:
            return time_base
        return time_base / modifier


class ChantierSpatial(Batiment):
    _base_cost = Cost(metal=400, cristal=200, deuterium=100)

    @property
    def base_cost(self) -> Cost:
        return self._base_cost


class UsineRobots(Batiment):
    _base_cost = Cost(metal=200, cristal=60, deuterium=100)

    @property
    def base_cost(self) -> Cost:
        return self._base_cost


class UsineNanites(Batiment):
    _base_cost = Cost(metal=1_000_000, cristal=500_000, deuterium=100_000)

    @property
    def base_cost(self) -> Cost:
        return self._base_cost


class Batiments:
    """Container des bâtiments d'une planète — attributs fixes, instances uniques."""
    def __init__(self, planet: 'Planet') -> None:
        self.chantier_spatial = ChantierSpatial(name='chantier_spatial', level=0)
        self.usine_robot = UsineRobots(name='usine_robot', level=0)
        self.usine_nanites = UsineNanites(name='usine_nanites', level=0)
        # lier chaque bâtiment à la planète
        for b in (self.chantier_spatial, self.usine_robot, self.usine_nanites):
            setattr(b, 'planet', planet)


class Planet:
    def __init__(self, name: str, coords: Tuple[int, int, int], is_main: bool = False):
        self.name = name
        self.coords = coords
        self.is_main = is_main
        # instancier le container fixe des bâtiments (tous niveaux 0 par défaut)
        self.batiments = Batiments(self)

    # compatibilité : méthode utilitaire pour récupérer par string si besoin
    def find_building(self, name: str) -> Optional[Batiment]:
        return getattr(self.batiments, name, None)


class Vaisseau:
    """Représentation minimale d'un vaisseau pour usage futur."""
    def __init__(self, type_name: str, base_build_time: float, ready: int = 0):
        self.type_name = type_name
        self.base_build_time = base_build_time
        self.ready = ready


# test rapide
if __name__ == '__main__':
    p = Planet('Mere', (1,1,1), is_main=True)
    # niveaux de test
    p.batiments.chantier_spatial.level = 11
    p.batiments.usine_robot.level = 2
    p.batiments.usine_nanites.level = 1
    print('chantier level:', p.batiments.chantier_spatial.level)
    print('usine robot level:', p.batiments.usine_robot.level)
    print('usine nanites level:', p.batiments.usine_nanites.level)
    print('build time chantier lvl11:', p.batiments.chantier_spatial.build_time(11))
