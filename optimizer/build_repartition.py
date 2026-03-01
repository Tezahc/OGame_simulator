import logging
from typing import Dict, List, Tuple
from sympy import Rational, symbols, Eq, solve, Symbol

"""Side project de calcul de répartition de liste de construction entre plusieurs planètes.
les équations représentent le total à produire (qty) tandis que les autres expriment le temps de construction dans le chantier spatial + le temps de vol pour ce vaisseau jusqu'à la planète mère.

l'enjeu étant que si le trajet est trop long, la planète devrait être exclue de la production sans compromettre le système d'équations.
"""

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s (%(filename)s:%(lineno)d)')

def solve_for_negatives(included :List[Symbol], total :int) -> Tuple[Dict[Symbol, Rational], List[Symbol]]:
    """Résout le système pour la liste `included` et retourne (sol_dict, negatives_list).
    - sol_dict: dict symbole ->expr ou None si pas de solution
    - negatives_list: liste des symboles (sauf `a`) dont la solution est < 0"""
    qty = Eq(sum(included), total)
    equations = [qty] + [EQ_MAPS[s] for s in included if s != a]
    raw = solve(equations, included)

    if not raw:
        return None, []
    if isinstance(raw, list):
        logging.warning(f"L'output de raw n'est pas un dictionnaire, comme attendu. {raw}")
        solution = raw[0]
    else: 
        solution = raw

    negatives = [s for s in included if s != a and solution.get(s, 0) < 0]
    return solution, negatives


# Variables
a, b, c, d = symbols("a b c d")
included_ini = [a, b, c, d]
included = included_ini.copy()

# Equations associées aux planètes (b, c, d). a est la planète mère (toujours gardée).
EQ_MAPS = {
    b: Eq(4*a, 30*b + 500),
    c: Eq(4*a, 9*c + 1075),
    d: Eq(4*a, 22*d + 501),
}
TOTAL = 148

solution, negatives = solve_for_negatives(included_ini, TOTAL)

# Boucle basée sur la présence de solutions négatives
while negatives:
    # retirer toutes les variables négatives
    included = [qty for qty in included if qty not in negatives]

    solution, negatives = solve_for_negatives(included, TOTAL)

    if solution is None:
        print("Pas de solution trouvée après exclusion.")
        break
    
# result = dict.fromkeys(included_ini, 0)
result = {planet: int(round(solution[planet].evalf())) for planet in included_ini}

print(result)
