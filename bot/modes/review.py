from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from db import queries
import say
import menu
from modes import modes
from modes.modes import choose_pack
from utils import send, user
import utils
from random import shuffle
from user_states import states
from modes.modes import ConversationStates


class ReviewTypes:
    TRUST = "Trust"
    ENTER = "Enter"
    TEST = "Test"
    PRACTICE = "Practice"

review_types_markup = [ReviewTypes.TRUST, ReviewTypes.ENTER]

languages = ["Front", "Back"]
practice_markup = ["Proceed"]

trust_markup = ["Right", "Wrong", "/change_language"]
start_markup = ["Start!"]


class Card:
    def __init__(self, c):
        self.side = c[1:3]
        self.id = c[0]


class ReviewState:
    def __init__(self, type, cards):
        self.cards = []
        for c in cards:
            self.cards.append(Card(c))
        self.right_answers = []
        self.wrong_answers = []
        self.type = type
        self.language = 0
        self.first_go = True
        self.last_card = None

    def move(self, update):
        self.cards = self.wrong_answers
        self.wrong_answers = []
        if self.first_go and self.type != ReviewTypes.PRACTICE:
            for i in self.right_answers:
                queries.update_card_data(user(update), i.id, 1)
        for i in self.wrong_answers:
            queries.update_card_data(user(update), i.id, 0)
        self.first_go = False
        self.shuffle()

    def ask(self):
        return self.next().side[self.language]

    def answer(self):
        return "Answer: " + (self.last_card or self.next()).side[not self.language]

    def right(self, update, printing=False):
        if printing:
            send(update, say.right)
        self.right_answers.append(self.last_card)

    def wrong(self, update, true_ans):
        if true_ans:
            send(update, say.wrong(true_ans))
        self.wrong_answers.append(self.last_card)

    def shuffle(self):
        shuffle(self.cards)

    def next(self):
        return self.cards[0]

    def pop(self):
        self.cards.pop(0)

    def compare(self, s):
        answer = self.last_card.side[not self.language]
        if s == answer:
            return None
        return answer

    def test_markup(self):
        answers = [self.next().side[not self.language]]
        for i in (self.cards + self.right_answers + self.wrong_answers):
            if i != self.next():
                answers.append(i.side[not self.language])
        shuffle(answers[1:])
        answers = answers[:3]
        shuffle(answers)
        return answers

    def store(self):
        self.last_card = self.next()
        self.pop()


def init_review(bot, update):
    states[user(update)] = ReviewState(ReviewTypes.TRUST, states[user(update)])
    return choose_review_type(bot, update)


def init_test(bot, update):
    states[user(update)] = ReviewState(ReviewTypes.TEST, states[user(update)])
    return choose_language(bot, update)


def init_practice(bot, update):
    states[user(update)] = ReviewState(ReviewTypes.PRACTICE, states[user(update)])
    return choose_language(bot, update)


def choose_review_type(bot, update):
    send(update, say.choose_type_of_review, markup=review_types_markup)
    return ConversationStates.CHOOSE_REVIEW_TYPE


def review_type_chosen(bot, update):
    if update.message.text not in review_types_markup:
        send(update, say.incorrect_input, markup=review_types_markup)
        return choose_review_type(bot, update)
    states[user(update)].type = update.message.text
    return choose_language(bot, update)


def choose_language(bot, update):
    send(update, say.choose_language(states[user(update)].cards[0]), markup=languages)
    return ConversationStates.CHOOSE_LANGUAGE


def language_chosen(bot, update):
    if update.message.text not in languages:
        send(update, say.incorrect_input)
        return choose_language(bot, update)
    states[user(update)].language = (0 if update.message.text == languages[0] else 1)
    states[user(update)].shuffle()
    return ask(bot, update) if states[user(update)].type != ReviewTypes.TRUST else ask(bot, update, start_markup)


def ask(bot, update, special_markup=None):
    if states[user(update)].type == ReviewTypes.TRUST:
        opts = trust_markup
    elif states[user(update)].type == ReviewTypes.ENTER:
        opts = None
    elif states[user(update)].type == ReviewTypes.TEST:
        opts = states[user(update)].test_markup()
    else:
        opts = practice_markup

    send(update, states[user(update)].ask(), markup=(special_markup or opts))

    if states[user(update)].type != ReviewTypes.TRUST:
        states[user(update)].store()
    return ConversationStates.ITERATE


def check(bot, update):
    if states[user(update)].type == ReviewTypes.TRUST:
        return trust_check(bot, update)
    if states[user(update)].type == ReviewTypes.PRACTICE:
        states[user(update)].right(update)
    else:
        true_ans = states[user(update)].compare(update.message.text.strip())
        if not true_ans:
            states[user(update)].right(update)
        else:
            states[user(update)].wrong(update, true_ans)
    if not states[user(update)].cards:
        return end(bot, update)
    return ask(bot, update)


def trust_check(bot, update):
    if update.message.text == start_markup[0]:
        pass
    elif update.message.text == trust_markup[0]:
        states[user(update)].right(update)
    else:
        states[user(update)].wrong(update, None)
    states[user(update)].store()
    send(update, states[user(update)].answer())
    if not states[user(update)].cards:
        return end(bot, update)
    return ask(bot, update)


def end(bot, update):
    if not states[user(update)].wrong_answers:
        send(update, say.completed)
        review_quit(bot, update)
        return ConversationStates.QUIT
    send(update, say.inter_results(len(states[user(update)].right_answers), len(states[user(update)].wrong_answers)))
    states[user(update)].move(update)
    return ask(bot, update)


def change_language(bot, update):
    states[user(update)].language = not states[user(update)].language
    return ask(bot, update)


def review_quit(bot, update):
    try:
        states.pop(user(update))
    except KeyError:
        pass
    # send(update, "Quitting...")
    menu.head_menu(bot, update)
    return ConversationHandler.END
