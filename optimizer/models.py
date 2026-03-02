"""Modèles POO (refacto minimal) pour l'outil de répartition.

Conventions appliquées ici :
- `Batiment` fournit la méthode générique `cost_at_level(level)` et `build_time(level)`.
- Les coûts de base sont obligatoires pour chaque sous-classe : implémentation via
  une propriété `base_cost` abstraite que la sous-classe doit définir.
- Les coûts sont exposés via la petite structure `Cost` pour permettre `cost.metal`.
- Planet propose un wrapper `build_time_for(name, level)` comme façade pratique.
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

    `build_time` est défini par défaut ici à partir des coûts ; les sous-classes
    peuvent redéfinir la méthode si nécessaire.
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
        """Calcul simple du temps de construction basé sur la somme des coûts métal+cristal.

        Formula: (metal + cristal) / (2500 * max(4 - level/2, 1))
        - placé ici parce que le calcul utilise uniquement les coûts propres au bâtiment.
        - Planet pourra rester la source de vérité pour composer effets d'autres bâtiments
          et ajouter des temps de trajet ; mais le calcul de base du batiment appartient
          logiquement au Batiment lui-même.
        """
        costs = self.cost_at_level(level)
        return (costs.metal + costs.cristal) / (2500 * max(4 - level / 2, 1))


class ChantierSpatial(Batiment):
    """Chantier spatial : définit seulement les coûts de base pour le chantier.
    """

    _base_cost = Cost(metal=400, cristal=200, deuterium=100)

    @property
    def base_cost(self) -> Cost:
        return self._base_cost


class Planet:
    """Représentation minimale d'une planète.

    Fournit une façade `build_time_for(name, level)` pour obtenir le temps de
    construction du bâtiment nommé sur cette planète sans avoir à manipuler
    explicitement l'instance de bâtiment.
    """

    def __init__(self, name: str, coords: Tuple[int, int, int], is_main: bool = False):
        self.name = name
        self.coords = coords
        self.is_main = is_main
        self.buildings: List[Batiment] = []

    def add_building(self, b: Batiment) -> None:
        self.buildings.append(b)

    def find_building(self, name: str) -> Optional[Batiment]:
        for b in self.buildings:
            if b.name == name:
                return b
        return None

    def build_time_for(self, name: str, level: int) -> float:
        """Façade pratique : récupère le bâtiment par `name` et appelle sa méthode `build_time`.

        Usage recommandé : `planet.build_time_for('Chantier', level)` ou
        `planet.find_building('Chantier').build_time(level)` si tu veux travailler
        directement avec l'instance.
        """
        b = self.find_building(name)
        if b is None:
            raise ValueError(f"Bâtiment '{name}' introuvable sur la planète {self.name}")
        return b.build_time(level)


class Vaisseau:
    """Représentation minimale d'un vaisseau pour usage futur."""
    def __init__(self, type_name: str, base_build_time: float, ready: int = 0):
        self.type_name = type_name
        self.base_build_time = base_build_time
        self.ready = ready


# test rapide si exécuté directement
if __name__ == '__main__':
    cs = ChantierSpatial(name='Chantier', level=3)
    p = Planet('Mere', (1,1,1), is_main=True)
    p.add_building(cs)
    print('cost level3:', cs.cost_at_level(3))
    print('build time (chantier level 3) via Batiment:', cs.build_time(3))
    print('build time via Planet facade:', p.build_time_for('Chantier', 3))
