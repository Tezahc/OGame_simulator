"""Modèles POO (refacto minimal) pour l'outil de répartition.

Conventions appliquées ici :
- `Batiment` fournit la méthode générique `cost_at_level(level)`.
- Les coûts de base sont obligatoires pour chaque sous-classe : implémentation via
  une propriété `base_cost` abstraite que la sous-classe doit définir.
- Les coûts sont exposés via la petite structure `Cost` pour permettre `cost.metal`.
- Suppression des helpers liés aux vaisseaux/temps de construction pour l'instant.
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

    Remarque sur `max(1, level)`: la formule calcule le coût pour "passer au niveau N" en
    appliquant `base * growth**(N-1)`. Si `level` vaut 0 ou une valeur négative, on
    considère le niveau minimal 1 pour éviter exposants négatifs ou coûts non-sens.
    Cela garantit que `cost_at_level(1)` == `base_cost`.
    """

    name: str
    level: int = 0
    growth: float = 2.0

    @property
    @abstractmethod
    def base_cost(self) -> Cost:
        """Doit être implémentée par la sous-classe pour fournir les coûts de base."""
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
        """Calcule le coût pour une ressource à partir d'un `base` et d'un exposant.

        Cette méthode utilise `self.growth` (qui peut varier par instance) et peut
        accéder à `self` si nécessaire. Elle n'est plus un `@staticmethod` pour
        permettre l'utilisation de l'état d'instance si souhaité.
        """
        return base * (self.growth ** exponent)


class ChantierSpatial(Batiment):
    """Chantier spatial : définit seulement les coûts de base pour le chantier.

    La classe ne contient volontairement pas de logique de temps de construction
    des vaisseaux pour l'instant (on y reviendra plus tard).
    """

    # coûts de base (niveau 1) : à personnaliser ici (immutable via Cost)
    _base_cost = Cost(metal=400, cristal=200, deuterium=100)

    @property
    def base_cost(self) -> Cost:
        return self._base_cost


class Planet:
    """Représentation minimale d'une planète.

    On évite de créer des getters spécialisés (ex: `get_chantier`) ; on expose
    simplement la liste `buildings` et une méthode utilitaire `find_building`.
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


class Vaisseau:
    """Représentation minimale d'un vaisseau pour usage futur.

    On n'implémente pas la logique de temps de construction ici (remplacée plus tard
    par la logique qui composera les bâtiments de la planète).
    """
    def __init__(self, type_name: str, base_build_time: float, ready: int = 0):
        self.type_name = type_name
        self.base_build_time = base_build_time
        self.ready = ready


# exemples rapides (non obligatoires)
if __name__ == '__main__':
    cs = ChantierSpatial(name='Chantier', level=3)
    print('base cost:', cs.base_cost)
    print('cost to reach level 3:', cs.cost_at_level(3))
