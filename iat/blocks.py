"""Setup of rounds
Categories are configured in session config like:
```primary = ['male', 'female'], secondary = ['work', 'family']```
Numbers in block config corresponds to 1st and 2nd element of corresponding pair
"""
import copy

# classic setup
# primary category switches, secondary stays in place
BLOCKS1 = {
    # Rondas 1 a 7 (ya existentes)
    1: {
        'title': "Round 1 (practice)",
        'practice': True,
        'left': {'primary': 1},  # felidae
        'right': {'primary': 2},  # canidae
    },
    2: {
        'title': "Round 2 (practice)",
        'practice': True,
        'left': {'secondary': 1},  # positive
        'right': {'secondary': 2},  # negative
    },
    3: {
        'title': "Round 3",
        'practice': False,
        'left': {'primary': 1, 'secondary': 1},  # felidae + positive
        'right': {'primary': 2, 'secondary': 2},  # canidae + negative
    },
    4: {
        'title': "Round 4",
        'practice': False,
        'left': {'primary': 1, 'secondary': 1},  # felidae + positive
        'right': {'primary': 2, 'secondary': 2},  # canidae + negative
    },
    5: {
        'title': "Round 5 (practice)",
        'practice': True,
        'left': {'primary': 2},  # canidae
        'right': {'primary': 1},  # felidae
    },
    6: {
        'title': "Round 6",
        'practice': False,
        'left': {'primary': 2, 'secondary': 1},  # canidae + positive
        'right': {'primary': 1, 'secondary': 2},  # felidae + negative
    },
    7: {
        'title': "Round 7",
        'practice': False,
        'left': {'primary': 2, 'secondary': 1},  # canidae + positive
        'right': {'primary': 1, 'secondary': 2},  # felidae + negative
    },
    # Rondas 8 a 14 (nuevas)
    8: {
        'title': "Round 8 (practice)",
        'practice': True,
        'left': {'primary': 3},  # male
        'right': {'primary': 4},  # female
    },
    9: {
        'title': "Round 9 (practice)",
        'practice': True,
        'left': {'secondary': 1},  # positive
        'right': {'secondary': 2},  # negative
    },
    10: {
        'title': "Round 10",
        'practice': False,
        'left': {'primary': 3, 'secondary': 1},  # male + positive
        'right': {'primary': 4, 'secondary': 2},  # female + negative
    },
    11: {
        'title': "Round 11",
        'practice': False,
        'left': {'primary': 3, 'secondary': 1},  # male + positive
        'right': {'primary': 4, 'secondary': 2},  # female + negative
    },
    12: {
        'title': "Round 12 (practice)",
        'practice': True,
        'left': {'primary': 4},  # female
        'right': {'primary': 3},  # male
    },
    13: {
        'title': "Round 13",
        'practice': False,
        'left': {'primary': 4, 'secondary': 1},  # female + positive
        'right': {'primary': 3, 'secondary': 2},  # male + negative
    },
    14: {
        'title': "Round 14",
        'practice': False,
        'left': {'primary': 4, 'secondary': 1},  # female + positive
        'right': {'primary': 3, 'secondary': 2},  # male + negative
    },
# e.g: male vs female
    8: {
        'title': "Round 8 (practice)",
        'practice': True,
        'left': {'primary': 3},
        'right': {'primary': 4},
    },
    # e.g: work vs family
    9: {
        'title': "Round 9 (practice)",
        'practice': True,
        'left': {'secondary': 1},
        'right': {'secondary': 2},
    },
    # e.g: male+work vs female+family
    10: {
        'title': "Round 10",
        'practice': False,
        'left': {'primary': 3, 'secondary': 1},
        'right': {'primary': 4, 'secondary': 2},
    },
    11: {
        'title': "Round 11",
        'practice': False,
        'left': {'primary': 3, 'secondary': 1},
        'right': {'primary': 4, 'secondary': 2},
    },
    # e.g: female vs male
    12: {
        'title': "Round 12 (practice)",
        'practice': True,
        'left': {'primary': 4},
        'right': {'primary': 2},
    },
    # e.g: female+work vs male+family
    13: {
        'title': "Round 13",
        'practice': False,
        'left': {'primary': 4, 'secondary': 1},
        'right': {'primary': 3, 'secondary': 2},
    },
    14: {
        'title': "Round 14",
        'practice': False,
        'left': {'primary': 4, 'secondary': 1},
        'right': {'primary': 3, 'secondary': 2},
    },
    15: {  # Definición para la ronda 15 (FeedbackIAT y Results)
            'title': "Round 15 (FeedbackIAT, results, game)",
            'practice': False,
            'left': {
                'primary': '',  # Cadena vacía para evitar conflictos
                'secondary': ''
            },
            'right': {
                'primary': '',
                'secondary': ''
            }
        },
    16: {  # Definición para la ronda 15 (FeedbackIAT y Results)
        'title': "Round 16 (game)",
        'practice': False,
        'left': {
            'primary': '',  # Cadena vacía para evitar conflictos
            'secondary': ''
        },
        'right': {
            'primary': '',
            'secondary': ''
        }
    },
    17: {  # Definición para la ronda 15 (FeedbackIAT y Results)
        'title': "Round 17 (game)",
        'practice': False,
        'left': {
            'primary': '',  # Cadena vacía para evitar conflictos
            'secondary': ''
        },
        'right': {
            'primary': '',
            'secondary': ''
        }
    },
    18: {  # Definición para la ronda 15 (FeedbackIAT y Results)
        'title': "Round 18 (game)",
        'practice': False,
        'left': {
            'primary': '',  # Cadena vacía para evitar conflictos
            'secondary': ''
        },
        'right': {
            'primary': '',
            'secondary': ''
        }
    },
    19: {  # Definición para la ronda 15 (FeedbackIAT y Results)
        'title': "Agradecimiento",
        'practice': False,
        'left': {
            'primary': '',  # Cadena vacía para evitar conflictos
            'secondary': ''
        },
        'right': {
            'primary': '',
            'secondary': ''
        }
    }


}


# alternative setup
# primary category stays in place, secondary switches
BLOCKS2 = {
    # e.g: male vs female
    1: {
        'title': "Round 1 (practice)",
        'practice': True,
        'left': {'primary': 1},
        'right': {'primary': 2},
    },
    # e.g: work vs family
    2: {
        'title': "Round 2 (practice)",
        'practice': True,
        'left': {'secondary': 1},
        'right': {'secondary': 2},
    },
    # e.g: male+work vs female+family
    3: {
        'title': "Round 3",
        'practice': False,
        'left': {'primary': 1, 'secondary': 1},
        'right': {'primary': 2, 'secondary': 2},
    },
    4: {
        'title': "Round 4",
        'practice': False,
        'left': {'primary': 1, 'secondary': 1},
        'right': {'primary': 2, 'secondary': 2},
    },
    # e.g: family vs work
    5: {
        'title': "Round 5 (practice)",
        'practice': True,
        'left': {'secondary': 2},
        'right': {'secondary': 1},
    },
    # e.g: male+family vs female+work
    6: {
        'title': "Round 6",
        'practice': False,
        'left': {'primary': 1, 'secondary': 2},
        'right': {'primary': 2, 'secondary': 1},
    },
    7: {
        'title': "Round 7",
        'practice': False,
        'left': {'primary': 1, 'secondary': 2},
        'right': {'primary': 2, 'secondary': 1},
    },
}
BLOCKS = BLOCKS1

def configure(block, config):
    """Insertar nombres de categorías desde la configuración en el setup del bloque.
    block: {'left': {'primary': 1, 'secondary': 1}, 'right': {'primary': 2, 'secondary': 2}}
    config: {'primary': ['maledsadsa', 'female'], 'secondary': ['work', 'family']}
    result: {'left': {'primary': 'male', 'secondary': 'work'}, 'right': {'primary': 'female', 'secondary': 'family'}}
    """
    result = copy.deepcopy(block)
    for side in ['left', 'right']:
        for cls, idx in block[side].items():
            if isinstance(idx, int):
                try:
                    # Asegurarse de que el índice esté dentro del rango
                    result[side][cls] = config[cls][idx - 1]
                except (IndexError, KeyError):
                    # Si el índice está fuera de rango o la clave no existe, asignar una cadena vacía
                    result[side][cls] = ''
            else:
                # Si idx no es un entero, asignar una cadena vacía o manejarlo según tu lógica
                result[side][cls] = ''
    return result
