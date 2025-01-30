import time
import random
# from .admin_report_functions import *
from otree.api import *
from otree import settings
from . import stimuli
from . import stats
from . import blocks
import math
from statistics import mean, stdev
from decimal import Decimal


doc = """
Implicit Association Test, draft
"""
from statistics import mean, stdev

def dscore1(data3: list, data4: list, data6: list, data7: list):
    # Filtrar valores demasiado largos.
    def not_long(value):
        return value < 10.0

    data3 = list(filter(not_long, data3))
    data4 = list(filter(not_long, data4))
    data6 = list(filter(not_long, data6))
    data7 = list(filter(not_long, data7))

    # Filtrar valores demasiado cortos
    def too_short(value):
        return value < 0.300

    total_data = data3 + data4 + data6 + data7
    short_data = list(filter(too_short, total_data))

    if len(total_data) == 0 or (len(short_data) / len(total_data) > 0.1):
        return None

    # Calcular el d-score
    combined_3_6 = data3 + data6
    combined_4_7 = data4 + data7

    if len(combined_3_6) < 2 or len(combined_4_7) < 2:
        # stdev requiere al menos dos datos
        return None

    std_3_6 = stdev(combined_3_6)
    std_4_7 = stdev(combined_4_7)

    mean_3_6 = mean(data6) - mean(data3) if len(data6) > 0 and len(data3) > 0 else 0
    mean_4_7 = mean(data7) - mean(data4) if len(data7) > 0 and len(data4) > 0 else 0

    dscore_3_6 = mean_3_6 / std_3_6 if std_3_6 > 0 else 0
    dscore_4_7 = mean_4_7 / std_4_7 if std_4_7 > 0 else 0

    dscore_mean1 = (dscore_3_6 + dscore_4_7) * 0.5
    return dscore_mean1


def dscore2(data10: list, data13: list, data11: list, data14: list):
    # Filtrar valores demasiado largos
    def not_long(value):
        return value < 10.0

    data10 = list(filter(not_long, data10))
    data13 = list(filter(not_long, data13))
    data11 = list(filter(not_long, data11))
    data14 = list(filter(not_long, data14))

    # Filtrar valores demasiado cortos
    def too_short(value):
        return value < 0.300

    total_data = data10 + data13 + data11 + data14
    short_data = list(filter(too_short, total_data))

    if len(total_data) == 0 or (len(short_data) / len(total_data) > 0.1):
        return None

    # Calcular el d-score
    combined_10_11 = data10 + data11
    combined_13_14 = data13 + data14

    if len(combined_10_11) < 2 or len(combined_13_14) < 2:
        # stdev requiere al menos dos datos
        return None

    std_10_11 = stdev(combined_10_11)
    std_13_14 = stdev(combined_13_14)

    mean_10_11 = mean(data11) - mean(data10) if len(data11) > 0 and len(data10) > 0 else 0
    mean_13_14 = mean(data14) - mean(data13) if len(data14) > 0 and len(data13) > 0 else 0

    dscore_10_11 = mean_10_11 / std_10_11 if std_10_11 > 0 else 0
    dscore_13_14 = mean_13_14 / std_13_14 if std_13_14 > 0 else 0

    dscore_mean2 = (dscore_10_11 + dscore_13_14) * 0.5
    return dscore_mean2


class Constants(BaseConstants):
    name_in_url = 'iat'
    players_per_group = None  # Mantener 2 para juegos del dictador
    num_rounds = 18  # 14 para IAT + 4 para dictador

    keys = {"f": 'left', "j": 'right'}
    trial_delay = 0.250
    endowment = Decimal('100')  # Añadido para dictador
    categories = ['perro', 'gato', 'blanco', 'negro']  # Categorías para el Dictador

def url_for_image(filename):
    return f"/static/images/{filename}"

class Subsession(BaseSubsession):
    practice = models.BooleanField()
    primary_left = models.StringField()
    primary_right = models.StringField()
    secondary_left = models.StringField()
    secondary_right = models.StringField()

def creating_session(self):
    session = self.session
    defaults = dict(
        retry_delay=0.5,
        trial_delay=0.5,
        primary=[None, None],
        primary_images=False,
        secondary=[None, None],
        secondary_images=False,
        num_iterations={
            # Rondas existentes para IAT
            1: 5, 2: 5, 3: 10, 4: 20, 5: 5, 6: 10, 7: 20,
            8: 5, 9: 5, 10: 10, 11: 20, 12: 5, 13: 10, 14: 20,
            # Rondas adicionales para Dictador
            15: 1, 16: 1, 17: 1, 18: 1
        },
    )
    session.params = {}
    for param in defaults:
        session.params[param] = session.config.get(param, defaults[param])

    block = get_block_for_round(self.round_number, session.params)

    self.practice = block.get('practice', False)
    self.primary_left = block.get('left', {}).get('primary', "")
    self.primary_right = block.get('right', {}).get('primary', "")
    self.secondary_left = block.get('left', {}).get('secondary', "")
    self.secondary_right = block.get('right', {}).get('secondary', "")

    # Asignar orden de rondas del IAT solo en la primera ronda
    if self.round_number == 1:
        for player in self.get_players():
            iat_ordering = random.choice([
                list(range(1, 15)),  # Orden directo: 1-14
                list(range(8, 15)) + list(range(1, 8))  # Orden invertido: 8-14,1-7
            ])
            player.participant.vars['iat_round_order'] = iat_ordering

        # Aleatorizar las categorías del Dictador para las rondas 15-18
        shuffled_categories = Constants.categories.copy()
        random.shuffle(shuffled_categories)
        session.vars['shuffled_dictator_categories'] = shuffled_categories

    # Asignar categorías al Dictador basadas en la lista aleatoria para las rondas 15-18
    if self.round_number in [15, 16, 17, 18]:
        shuffled_categories = session.vars.get('shuffled_dictator_categories')
        if shuffled_categories:
            # Asignar una categoría por ronda 15-18 al grupo
            assigned_category = shuffled_categories[self.round_number - 15]
            for group in self.get_groups():
                group.dictator_category = assigned_category

def get_block_for_round(rnd, params):
    """Get a round setup from BLOCKS with actual categories' names substituted from session config"""
    if rnd in blocks.BLOCKS:
        block = blocks.BLOCKS[rnd]
        result = blocks.configure(block, params)
        return result
    else:
        # Retorna un bloque vacío o predeterminado para rondas que no lo necesitan
        return {}

def thumbnails_for_block(block, params):
    """Return image urls for each category in block.
    Taking first image in the category as a thumbnail.
    """
    thumbnails = {'left': {}, 'right': {}}
    for side in ['left', 'right']:
        for cls in ['primary', 'secondary']:
            if cls in block[side] and params[f"{cls}_images"]:
                # use first image in categopry as a corner thumbnail
                images = stimuli.DICT[block[side][cls]]
                thumbnails[side][cls] = url_for_image(images[0])
    return thumbnails


def labels_for_block(block):
    """Return category labels for each category in block
    Just stripping prefix "something:"
    """
    labels = {'left': {}, 'right': {}}
    for side in ['left', 'right']:
        for cls in ['primary', 'secondary']:
            if cls in block[side]:
                cat = block[side][cls]
                if ':' in cat:
                    labels[side][cls] = cat.split(':')[1]
                else:
                    labels[side][cls] = cat
    return labels


def get_num_iterations_for_round(rnd):
    """Get configured number of iterations
    The rnd: Player or Subsession
    """
    idx = rnd.round_number
    num = rnd.session.params['num_iterations'][idx]
    return num

class Player(BasePlayer):
    iteration = models.IntegerField(initial=0)  # Contador para iteraciones del jugador
    num_trials = models.IntegerField(initial=0)  # Número total de intentos del jugador
    num_correct = models.IntegerField(initial=0)  # Número de respuestas correctas
    num_failed = models.IntegerField(initial=0)  # Número de respuestas incorrectas
    name = models.StringField(label="Nombre")
    age = models.IntegerField(label="Edad", min=0, max=99)
    sports = models.StringField(
        widget=widgets.RadioSelect,
        choices=[
            ('Football', 'Football'),
            ('Basketball', 'Basketball'),
            ('Tennis', 'Tennis'),
            ('Swimming', 'Swimming'),
            ('Other', 'Other'),
        ],
        label="¿Cuál es tu deporte favorito?"
    )
    random_number = models.IntegerField(label="Número aleatorio entre 1 y 20", min=1, max=20)
    dscore1 = models.FloatField()  # D-score del primer IAT
    dscore2 = models.FloatField()  # D-score del segundo IAT

    # Nuevo campo para la pregunta moral
    moral_question = models.StringField(label="Aquí va una pregunta moral", blank=True)

    iat1_self_assessment = models.StringField(
        label="¿Cómo crees que te fue en el IAT 1 de male y female?",
        choices=[
            "Asociación leve a male+feliz, female+triste",
            "Asociación leve a male+triste, female+feliz",
            "Asociación moderada a male+feliz, female+triste",
            "Asociación moderada a male+triste, female+feliz",
            "Asociación fuerte a male+feliz, female+triste",
            "Asociación fuerte a male+triste, female+feliz",
        ],
        widget=widgets.RadioSelect
    )

    # Respuesta de autoevaluación para el IAT 2 (Ejemplo: Gato y Perro)
    iat2_self_assessment = models.StringField(
        label="¿Cómo crees que te fue en el IAT 2 de gato y perro?",
        choices=[
            "Asociación leve a gato+feliz, perro+triste",
            "Asociación leve a gato+triste, perro+feliz",
            "Asociación moderada a gato+feliz, perro+triste",
            "Asociación moderada a gato+triste, perro+feliz",
            "Asociación fuerte a gato+feliz, perro+triste",
            "Asociación fuerte a gato+triste, perro+feliz",
        ],
        widget=widgets.RadioSelect
    )

    # Variables para el rango moralmente aceptable del IAT 1
    iat1_lower_limit = models.FloatField(
        label="¿Cuál es el límite inferior del rango moralmente aceptable para el IAT 1?",
        help_text="Debe estar entre -2 y 0.",
        min=-2,
        max=0
    )

    iat1_upper_limit = models.FloatField(
        label="¿Cuál es el límite superior del rango moralmente aceptable para el IAT 1?",
        help_text="Debe estar entre 0 y 2.",
        min=0,
        max=2
    )

    # Variables para el rango moralmente aceptable del IAT 2
    iat2_lower_limit = models.FloatField(
        label="¿Cuál es el límite inferior del rango moralmente aceptable para el IAT 2?",
        help_text="Debe estar entre -2 y 0.",
        min=-2,
        max=0
    )

    iat2_upper_limit = models.FloatField(
        label="¿Cuál es el límite superior del rango moralmente aceptable para el IAT 2?",
        help_text="Debe estar entre 0 y 2.",
        min=0,
        max=2
    )

    hide_iat1_info_in_range = models.BooleanField(
        label="¿Quieres que se esconda la información del IAT 1 para decisiones morales si está dentro de tu rango moralmente aceptable?",
        choices=[
            (True, "Sí"),
            (False, "No")
        ]
    )
    hide_iat1_info_out_of_range = models.BooleanField(
        label="¿Quieres que se esconda la información del IAT 1 para decisiones morales si está fuera de tu rango moralmente aceptable?",
        choices=[
            (True, "Sí"),
            (False, "No")
        ]
    )

    # Campos para ocultar información del IAT 2
    hide_iat2_info_in_range = models.BooleanField(
        label="¿Quieres que se esconda la información del IAT 2 para decisiones morales si está dentro de tu rango moralmente aceptable?",
        choices=[
            (True, "Sí"),
            (False, "No")
        ]
    )
    hide_iat2_info_out_of_range = models.BooleanField(
        label="¿Quieres que se esconda la información del IAT 2 para decisiones morales si está fuera de tu rango moralmente aceptable?",
        choices=[
            (True, "Sí"),
            (False, "No")
        ]
    )



    # Probabilidad asignada para IAT 1
    iat1_assessment_probability = models.IntegerField(
        label="¿Qué probabilidad le asignas a la veracidad de tu resultado en el IAT 1? (1-100)",
        min=1,
        max=100
    )

    # Probabilidad asignada para IAT 2
    iat2_assessment_probability = models.IntegerField(
        label="¿Qué probabilidad le asignas a la veracidad de tu resultado en el IAT 2? (1-100)",
        min=1,
        max=100
    )

    #campos para el juego del dictador.
    dictator_offer = models.CurrencyField(
        min=0,
        max=Constants.endowment,
        label="¿Cuánto te gustaría ofrecer?"
    )

class Group(BaseGroup):
    dictator_category = models.StringField(
        label="Categoría Asignada",
        doc="""Categoría a la que se asignará dinero en esta ronda."""
    )
    kept = models.CurrencyField(
        label="¿Cuánto deseas mantener para ti mismo?",
        min=0,
        max=Constants.endowment,
        doc="""Cantidad que el jugador decide mantener."""
    )
    assigned = models.CurrencyField(
        label="Asignación a la Categoría",
        min=0,
        max=Constants.endowment,
        doc="""Cantidad asignada a la categoría."""
    )

def get_actual_iat_round(player: Player):
    order = player.participant.vars.get('iat_round_order')
    if order and player.round_number <= 14:
        return order[player.round_number - 1]
    return player.round_number


def set_payoffs(group: Group):
    """
    Asigna los payoffs basados en la decisión del jugador.
    El jugador mantiene 'kept' y asigna el resto a la categoría.
    """
    kept = group.kept
    assigned = Constants.endowment - kept

    # Validar que la asignación sea correcta
    if assigned < 0 or kept < 0 or kept > Constants.endowment:
        # Manejar errores: asignar valores predeterminados o lanzar excepciones
        group.assigned = 0
        group.kept = Constants.endowment
    else:
        group.assigned = assigned

    # Asignar el payoff al jugador (manteniendo 'kept')
    for player in group.get_players():
        player.payoff = kept

class Trial(ExtraModel):
    """A record of single iteration
    Keeps corner categories from round setup to simplify furher analysis.
    The stimulus class is for appropriate styling on page.
    """

    player = models.Link(Player)
    round = models.IntegerField(initial=0)
    iteration = models.IntegerField(initial=0)
    timestamp = models.FloatField(initial=0)

    stimulus_cls = models.StringField(choices=('primary', 'secondary'))
    stimulus_cat = models.StringField()
    stimulus = models.StringField()
    correct = models.StringField(choices=('left', 'right'))

    response = models.StringField(choices=('left', 'right'))
    response_timestamp = models.FloatField()
    reaction_time = models.FloatField()
    is_correct = models.BooleanField()
    retries = models.IntegerField(initial=0)


def generate_trial(player: Player) -> Trial:
    """Create new question for a player"""
    block = get_block_for_round(player.round_number, player.session.params)
    chosen_side = random.choice(['left', 'right'])
    chosen_cls = random.choice(list(block[chosen_side].keys()))
    chosen_cat = block[chosen_side][chosen_cls]
    stimulus = random.choice(stimuli.DICT[chosen_cat])

    player.iteration += 1
    return Trial.create(
        player=player,
        iteration=player.iteration,
        timestamp=time.time(),
        #
        stimulus_cls=chosen_cls,
        stimulus_cat=chosen_cat,
        stimulus=stimulus,
        correct=chosen_side,
    )


def get_current_trial(player: Player):
    """Get last (current) question for a player"""
    trials = Trial.filter(player=player, iteration=player.iteration)
    if trials:
        [trial] = trials
        return trial


def encode_trial(trial: Trial):
    return dict(
        cls=trial.stimulus_cls,
        cat=trial.stimulus_cat,
        stimulus=url_for_image(trial.stimulus) if trial.stimulus.endswith((".png", ".jpg")) else str(trial.stimulus),
    )


def get_progress(player: Player):
    """Return current player progress"""
    return dict(
        num_trials=player.num_trials,
        num_correct=player.num_correct,
        num_incorrect=player.num_failed,
        iteration=player.iteration,
        total=get_num_iterations_for_round(player),
    )


def custom_export(players):
    yield [
        "session",
        "participant_code",
        "round",
        "primary_left",
        "primary_right",
        "secondary_left",
        "secondary_right",
        "iteration",
        "timestamp",
        "stimulus_class",
        "stimulus_category",
        "stimulus",
        "expected",
        "response",
        "is_correct",
        "reaction_time",
        "dictator_category",
        "dictator_offer",
        "assigned",
        "kept",
        "payoff"

    ]
    for p in players:
        if p.round_number not in (3, 4, 6, 7, 10, 11, 13, 14, 15, 16, 17, 18):
            continue
        participant = p.participant
        session = p.session
        subsession = p.subsession
        group = p.group
        for z in Trial.filter(player=p):
            yield [
                session.code,
                participant.code,
                subsession.round_number,
                subsession.primary_left,
                subsession.primary_right,
                subsession.secondary_left,
                subsession.secondary_right,
                z.iteration,
                z.timestamp,
                z.stimulus_cls,
                z.stimulus_cat,
                z.stimulus,
                z.correct,
                z.response,
                z.is_correct,
                z.reaction_time,
                p.dictator_category,
                p.dictator_offer,
                group.kept,
                group.dictator_category,
                group.assigned,
                p.payoff,
            ]

def play_game(player: Player, message: dict):
    """Main game workflow
    Implemented as reactive scheme: receive message from vrowser, react, respond.

    Generic game workflow, from server point of view:
    - receive: {'type': 'load'} -- empty message means page loaded
    - check if it's game start or page refresh midgame
    - respond: {'type': 'status', 'progress': ...}
    - respond: {'type': 'status', 'progress': ..., 'trial': data} -- in case of midgame page reload

    - receive: {'type': 'next'} -- request for a next/first trial
    - generate new trial
    - respond: {'type': 'trial', 'trial': data}

    - receive: {'type': 'answer', 'answer': ...} -- user answered the trial
    - check if the answer is correct
    - respond: {'type': 'feedback', 'is_correct': true|false} -- feedback to the answer

    When done solving, client should explicitely request next trial by sending 'next' message

    Field 'progress' is added to all server responses to indicate it on page.

    To indicate max_iteration exhausted in response to 'next' server returns 'status' message with iterations_left=0
    """
    session = player.session
    my_id = player.id_in_group
    ret_params = session.params
    max_iters = get_num_iterations_for_round(player)

    now = time.time()
    # the current trial or none
    current = get_current_trial(player)

    message_type = message['type']

    # print("iteration:", player.iteration)
    # print("current:", current)
    # print("received:", message)

    # page loaded
    if message_type == 'load':
        p = get_progress(player)
        if current:
            return {my_id: dict(type='status', progress=p, trial=encode_trial(current))}
        else:
            return {my_id: dict(type='status', progress=p)}

    # client requested new trial
    if message_type == "next":
        if current is not None:
            if current.response is None:
                raise RuntimeError("trying to skip over unsolved trial")
            if now < current.timestamp + ret_params["trial_delay"]:
                raise RuntimeError("retrying too fast")
            if current.iteration == max_iters:
                return {
                    my_id: dict(
                        type='status', progress=get_progress(player), iterations_left=0
                    )
                }
        # generate new trial
        z = generate_trial(player)
        p = get_progress(player)
        return {my_id: dict(type='trial', trial=encode_trial(z), progress=p)}

    # client gives an answer to current trial
    if message_type == "answer":
        if current is None:
            raise RuntimeError("trying to answer no trial")

        if current.response is not None:  # it's a retry
            if now < current.response_timestamp + ret_params["retry_delay"]:
                raise RuntimeError("retrying too fast")

            # undo last updation of player progress
            player.num_trials -= 1
            if current.is_correct:
                player.num_correct -= 1
            else:
                player.num_failed -= 1

        # check answer
        answer = message["answer"]

        if answer == "" or answer is None:
            raise ValueError("bogus answer")

        current.response = answer
        current.reaction_time = message["reaction_time"]
        current.is_correct = current.correct == answer
        current.response_timestamp = now

        # update player progress
        if current.is_correct:
            player.num_correct += 1
        else:
            player.num_failed += 1
        player.num_trials += 1

        p = get_progress(player)
        return {
            my_id: dict(
                type='feedback',
                is_correct=current.is_correct,
                progress=p,
            )
        }

    if message_type == "cheat" and settings.DEBUG:
        # generate remaining data for the round
        m = float(message['reaction'])
        if current:
            current.delete()
        for i in range(player.iteration, max_iters):
            t = generate_trial(player)
            t.iteration = i
            t.timestamp = now + i
            t.response = t.correct
            t.is_correct = True
            t.response_timestamp = now + i
            t.reaction_time = random.gauss(m, 0.3)
        return {
            my_id: dict(type='status', progress=get_progress(player), iterations_left=0)
        }

    raise RuntimeError("unrecognized message from client")


# PAGES

class Intro(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        # using 3rd block to take categories labels in instructions
        params = player.session.params
        block = get_block_for_round(3, params)
        return dict(
            params=params,
            labels=labels_for_block(block),
        )

class RoundN(Page):
    template_name = "iat/Main.html"

    @staticmethod
    def is_displayed(player: Player):
        # Mostrar solo en rondas de IAT
        return player.round_number <= 14

    @staticmethod
    def js_vars(player: Player):
        actual_round = get_actual_iat_round(player)
        return dict(
            params=player.session.params,
            keys=Constants.keys,
            actual_round=actual_round
        )

    @staticmethod
    def vars_for_template(player: Player):
        actual_round = get_actual_iat_round(player)
        params = player.session.params
        block = get_block_for_round(actual_round, params)
        return dict(
            params=params,
            block=block,
            thumbnails=thumbnails_for_block(block, params),
            labels=labels_for_block(block),
            num_iterations=get_num_iterations_for_round(player),
            DEBUG=settings.DEBUG,
            keys=Constants.keys,
            lkeys="/".join(
                [k for k in Constants.keys.keys() if Constants.keys[k] == 'left']
            ),
            rkeys="/".join(
                [k for k in Constants.keys.keys() if Constants.keys[k] == 'right']
            ),
        )

    live_method = play_game


class UserInfo(Page):
    form_model = 'player'
    form_fields = ['name', 'age', 'sports', 'random_number']

    @staticmethod
    def is_displayed(player):
        # Mostrar esta página solo una vez por participante
        return player.participant.vars.get('user_info_completed', False) == False

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Guardar valores en participant.vars si deseas usarlos globalmente
        participant = player.participant
        if not player.name:
            player.name = "Anónimo"
        if not player.age:
            player.age = 18
        if not player.sports:
            player.sports = "Sin especificar"
        if not player.random_number:
            player.random_number = 0

        # Marcar que la información ya fue recopilada
        participant.vars['user_info_completed'] = True

class PreguntaM(Page):
    form_model = 'player'
    form_fields = ['moral_question']

    @staticmethod
    def is_displayed(player):
        # Mostrar esta página solo una vez por participante
        return player.participant.vars.get('pregunta_moral_completada', False) == False

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Marcar que la página ya fue completada
        player.participant.vars['pregunta_moral_completada'] = True

    @staticmethod
    def error_message(player, values):
        # Validar que el campo moral_question no esté vacío
        if not values.get('moral_question'):
            return "Por favor, responde la pregunta antes de continuar."

class IATAssessmentPage(Page):
    form_model = 'player'
    form_fields = [
        'iat1_self_assessment',
        'iat2_self_assessment',
        'iat1_lower_limit',  # Límite inferior para el IAT 1
        'iat1_upper_limit',  # Límite superior para el IAT 1
        'iat2_lower_limit',  # Límite inferior para el IAT 2
        'iat2_upper_limit'   # Límite superior para el IAT 2
    ]

    @staticmethod
    def is_displayed(player):
        # Mostrar esta página solo en la ronda 15
        return player.round_number == 15

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        participant = player.participant

        # Validar y asignar valores predeterminados si es necesario
        if not player.iat1_self_assessment:
            player.iat1_self_assessment = "No especificado"
        if not player.iat2_self_assessment:
            player.iat2_self_assessment = "No especificado"

        # Marcar que la evaluación del IAT ya fue completada
        participant.vars['iat_assessment_completed'] = True

    @staticmethod
    def error_message(player, values):
        # Validar que todos los campos sean completados
        if not values.get('iat1_self_assessment'):
            return "Por favor, selecciona una opción para el IAT 1."
        if not values.get('iat2_self_assessment'):
            return "Por favor, selecciona una opción para el IAT 2."
        if values.get('iat1_lower_limit') is None:
            return "Por favor, ingresa un límite inferior para el rango moralmente aceptable del IAT 1."
        if values.get('iat1_upper_limit') is None:
            return "Por favor, ingresa un límite superior para el rango moralmente aceptable del IAT 1."
        if values['iat1_lower_limit'] >= values['iat1_upper_limit']:
            return "El límite inferior para el IAT 1 debe ser menor que el límite superior."
        if values.get('iat2_lower_limit') is None:
            return "Por favor, ingresa un límite inferior para el rango moralmente aceptable del IAT 2."
        if values.get('iat2_upper_limit') is None:
            return "Por favor, ingresa un límite superior para el rango moralmente aceptable del IAT 2."
        if values['iat2_lower_limit'] >= values['iat2_upper_limit']:
            return "El límite inferior para el IAT 2 debe ser menor que el límite superior."

class MoralDecisionPageCerteza(Page):
    form_model = 'player'
    form_fields = [
        'hide_iat1_info_in_range',      # Respuesta para IAT 1 dentro del rango
        'hide_iat1_info_out_of_range',  # Respuesta para IAT 1 fuera del rango
        'hide_iat2_info_in_range',      # Respuesta para IAT 2 dentro del rango
        'hide_iat2_info_out_of_range'   # Respuesta para IAT 2 fuera del rango
    ]

    @staticmethod
    def is_displayed(player):
        # Mostrar esta página solo en la ronda 15
        return player.round_number == 15

    @staticmethod
    def vars_for_template(player):
        user_range_iat1 = f"{player.iat1_lower_limit} a {player.iat1_upper_limit}"
        user_range_iat2 = f"{player.iat2_lower_limit} a {player.iat2_upper_limit}"
        return {
            'message_iat1_in_range': f"Si tu IAT 1 está en el rango definido por ti ({user_range_iat1}), ¿quieres que te escondamos la información contenida en el IAT 1 cuando tomes una decisión moral?",
            'message_iat1_out_of_range': f"Si tu IAT 1 está fuera del rango definido por ti ({user_range_iat1}), ¿quieres que te escondamos la información contenida en el IAT 1 cuando tomes una decisión moral?",
            'message_iat2_in_range': f"Si tu IAT 2 está en el rango definido por ti ({user_range_iat2}), ¿quieres que te escondamos la información contenida en el IAT 2 cuando tomes una decisión moral?",
            'message_iat2_out_of_range': f"Si tu IAT 2 está fuera del rango definido por ti ({user_range_iat2}), ¿quieres que te escondamos la información contenida en el IAT 2 cuando tomes una decisión moral?"
        }

class Results(Page):
    @staticmethod
    def is_displayed(player):
        # Mostrar la página de resultados en la ronda 14
        return player.round_number == 15

    @staticmethod
    def vars_for_template(player: Player):
        def extract(rnd):
            # Extraer tiempos de reacción de las rondas especificadas
            trials = [
                t
                for t in Trial.filter(player=player.in_round(rnd))
                if t.reaction_time is not None
            ]
            values = [t.reaction_time for t in trials]
            return values

        # Extraer datos para el primer IAT (rondas 3, 4, 6, 7)
        data3 = extract(3)
        data4 = extract(4)
        data6 = extract(6)
        data7 = extract(7)
        dscore1_result = dscore1(data3, data4, data6, data7)

        # Extraer datos para el segundo IAT (rondas 10, 13, 11, 14)
        data10 = extract(10)
        data13 = extract(13)
        data11 = extract(11)
        data14 = extract(14)
        dscore2_result = dscore2(data10, data13, data11, data14)

        # Guardar resultados en el jugador
        player.dscore1 = dscore1_result
        player.dscore2 = dscore2_result

        # Obtener combinaciones de pares positivos y negativos para el primer IAT
        pos_pairs_iat1 = labels_for_block(get_block_for_round(3, player.session.params))
        neg_pairs_iat1 = labels_for_block(get_block_for_round(6, player.session.params))

        # Obtener combinaciones de pares positivos y negativos para el segundo IAT
        pos_pairs_iat2 = labels_for_block(get_block_for_round(10, player.session.params))
        neg_pairs_iat2 = labels_for_block(get_block_for_round(13, player.session.params))

        # Validar si los resultados están dentro o fuera de los rangos definidos
        dscore1_in_range = (
                player.dscore1 >= player.iat1_lower_limit and
                player.dscore1 <= player.iat1_upper_limit
        )
        dscore2_in_range = (
                player.dscore2 >= player.iat2_lower_limit and
                player.dscore2 <= player.iat2_upper_limit
        )

        # Decidir si mostrar u ocultar resultados en base a las preferencias del usuario
        show_dscore1 = (
                (dscore1_in_range and not player.hide_iat1_info_in_range) or
                (not dscore1_in_range and not player.hide_iat1_info_out_of_range)
        )
        show_dscore2 = (
                (dscore2_in_range and not player.hide_iat2_info_in_range) or
                (not dscore2_in_range and not player.hide_iat2_info_out_of_range)
        )

        # Manejar valores del jugador
        player_name = player.field_maybe_none('name') or "Anónimo"
        player_age = player.field_maybe_none('age') or 18
        player_sports = player.field_maybe_none('sports') or "Sin especificar"
        player_random_number = player.field_maybe_none('random_number') or 0
        moral_question = player.field_maybe_none('moral_question') or "Sin respuesta"
        iat1_self_assessment = player.field_maybe_none('iat1_self_assessment') or "No especificado"
        iat1_assessment_probability = player.field_maybe_none('iat1_assessment_probability') or 0
        iat2_self_assessment = player.field_maybe_none('iat2_self_assessment') or "No especificado"
        iat2_assessment_probability = player.field_maybe_none('iat2_assessment_probability') or 0

        return dict(
            show_dscore1=show_dscore1,
            show_dscore2=show_dscore2,
            dscore1=dscore1_result if show_dscore1 else None,
            dscore2=dscore2_result if show_dscore2 else None,
            pos_pairs_iat1=pos_pairs_iat1,
            neg_pairs_iat1=neg_pairs_iat1,
            pos_pairs_iat2=pos_pairs_iat2,
            neg_pairs_iat2=neg_pairs_iat2,
            player_name=player_name,
            player_age=player_age,
            player_sports=player_sports,
            player_random_number=player_random_number,
            moral_question=moral_question,
            iat1_self_assessment=iat1_self_assessment,
            iat1_assessment_probability=iat1_assessment_probability,
            iat2_self_assessment=iat2_self_assessment,
            iat2_assessment_probability=iat2_assessment_probability,
        )

class DictatorIntroduction(Page):
    """
    Página de introducción al Juego del Dictador para la categoría asignada.
    """
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number in [15, 16, 17, 18]

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        # Asegurarse de que 'dictator_category' no sea None
        if group.dictator_category:
            category = group.dictator_category.capitalize()
        else:
            category = "Sin categoría asignada"
        return dict(
            category=category,
            endowment=Constants.endowment
        )

class DictatorOffer(Page):
    """
    Página donde el jugador decide cuánto mantener y cuánto asignar a la categoría.
    """
    form_model = 'group'
    form_fields = ['kept']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number in [15, 16, 17, 18]

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        return dict(
            category=group.dictator_category.capitalize(),
            endowment=Constants.endowment
        )

    @staticmethod
    def error_message(player, values):
        kept = values['kept']
        if kept < 0 or kept > Constants.endowment:
            return f"Por favor, ofrece una cantidad entre 0 y {Constants.endowment}."
        # No es necesario validar la suma aquí, ya que 'assigned' se calcula automáticamente

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        group = player.group
        set_payoffs(group)

class ResultsDictador(Page):
    @staticmethod
    def is_displayed(player):
        # Mostrar la página de resultados final solo en la última ronda (18)
        return player.round_number == 18

    @staticmethod
    def vars_for_template(player: Player):
        dictator_offers = []
        dictator_round_numbers = [15, 16, 17, 18]
        for rnd in dictator_round_numbers:
            p = player.in_round(rnd)
            assigned = p.group.assigned
            if assigned is None:
                assigned = 0  # O cualquier valor predeterminado que tenga sentido en tu contexto

            dictator_offers.append({
                'round': rnd,
                'category': p.group.field_maybe_none('dictator_category').capitalize() if p.group.field_maybe_none('dictator_category') else "Sin categoría asignada",
                'kept': p.group.kept,
                'assigned': assigned,
            })
        return dict(
            dictator_offers=dictator_offers
        )

page_sequence = [
    Intro,
    UserInfo,
    PreguntaM,
    RoundN,                     # Rondas 1-14: IAT
    IATAssessmentPage,          # Ronda 15: Evaluación del IAT
    MoralDecisionPageCerteza,   # Ronda 15: Decisión Moral
    Results,                    # Ronda 15: Resultados del IAT
    DictatorIntroduction,       # Rondas 16-18: Introducción al Dictador
    DictatorOffer,              # Rondas 16-18: Oferta del Dictador,    # Rondas 16-18: Espera de Resultados del Dictador
    ResultsDictador,            # Rondas 16-18: Resultados del Dictador,            # Ronda 18: Resultados Finales del Dictador
]