from sympy import symbols, Eq, solve
from sympy.abc import a, b, c, d

"""Side project de calcul de répartition de liste de construction entre plusieurs planètes.
les équations représentent le total à produire (qty) tandis que les autres expriment le temps de construction dans le chantier spatial + le temps de vol pour ce vaisseau jusqu'à la planète mère.

l'enjeu étant que si le trajet est trop long, la planète devrait être exclue de la production sans compromettre le système d'équations.
"""
# définition des équations de base
qty = Eq(a + b + c + d, 100)
eq1 = Eq(4*a, 30*b + 500)
eq2 = Eq(4*a, 9*c + 1075)
eq3 = Eq(4*a, 22*d + 501)

# système à résoudre
equations = [qty, eq1, eq2, eq3]

# résolution
solutions = solve(equations)


print(solutions)