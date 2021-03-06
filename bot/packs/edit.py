from telegram import ReplyKeyboardMarkup
from telegram.ext import ConversationHandler
import say
from utils import user, row_markup
from db import queries
from db.enums import *
from menu import head_menu

END = ConversationHandler.END
START = 0
CHOOSE_PACK = 1
CHOOSE_PACK_ACTION = 2
EDIT_PACK_NAME = 3
EDIT_PACK_PRIVACY = 4
EDIT_PACK_STATUS = 11
DELETE_PACK = 5
CHOOSE_CARD = 6
CHOOSE_CARD_ACTION = 7
EDIT_CARD_FRONT = 8
EDIT_CARD_BACK = 9
EDIT_CARD_STATUS = 10


_states = {}


# TODO: Add pages support
def start(bot, update):
    _states[user(update)] = {}
    return choose_pack(bot, update)


def end(bot, update):
    _states[user(update)] = None
    head_menu(bot, update)
    return END


def choose_pack(bot, update):
    packs = map(lambda x: str(x[0]) + ': ' + x[1], queries.active_packs(user(update)))
    update.message.reply_text(say.choose_pack, reply_markup=row_markup(packs))
    return CHOOSE_PACK


def choose_pack_h(bot, update):
    state = _states[user(update)]
    colon_ind = update.message.text.find(':')
    try:
        pack_id = int(update.message.text[:colon_ind])
    except ValueError:
        update.message.reply_text('Invalid')
        return CHOOSE_PACK
    state['pack_id'] = pack_id
    return choose_pack_action(bot, update)


def choose_pack_action(bot, update):
    state = _states[user(update)]
    pack_id = state['pack_id']
    pack_info = queries.get_pack(pack_id, user(update))

    if not queries.has_pack_read_access(pack_id, user(update)):
        update.message.reply_text(say.access_denied)
        return CHOOSE_PACK

    markup = []
    markup.append(['Do exercise', 'Show cards', 'Edit pack status'])
    if pack_info['owner_id'] == user(update):
        markup.append(['Edit name', 'Edit privacy', 'Delete pack'])

    update.message.reply_text(
        say.pack_info.format(pack_info['name'], pack_info['privacy'], pack_info['status']),
        reply_markup=ReplyKeyboardMarkup(markup, one_time_keyboard=True)
    )

    return CHOOSE_PACK_ACTION


def choose_pack_action_h(bot, update):
    state = _states[user(update)]
    text = update.message.text

    if text == 'Edit name':
        return edit_pack_name(bot, update)

    if text == 'Edit privacy':
        return edit_pack_privacy(bot, update)

    if text == 'Edit pack status':
        return edit_pack_status(bot, update)

    if text == 'Delete pack':
        return delete_pack(bot, update)

    if text == 'Do exercise':
        # TODO: Save selected pack id for /menu handler
        update.message.reply_text(say.not_implemented)

        update.message.reply_text(say.use_begin)
        return end(bot, update)

    if text == 'Show cards':
        return choose_card(bot, update)

    update.message.reply_text(say.not_recognized)
    return CHOOSE_PACK_ACTION


def edit_pack_name(bot, update):
    state = _states[user(update)]
    pack_info = queries.get_pack(state['pack_id'])
    if pack_info['owner_id'] != user(update):
        update.message.reply_text(say.access_denied)
        return CHOOSE_PACK_ACTION
    update.message.reply_text(say.choose_pack_name)
    return EDIT_PACK_NAME


def edit_pack_name_h(bot, update):
    state = _states[user(update)]
    pack_info = queries.get_pack(state['pack_id'])
    if pack_info['owner_id'] != user(update):
        update.message.reply_text(say.access_denied)
        return choose_pack_action(bot, update)
    queries.update_pack_name(state['pack_id'], update.message.text)
    update.message.reply_text(say.pack_name_updated)
    return choose_pack_action(bot, update)


def edit_pack_privacy(bot, update):
    state = _states[user(update)]
    pack_info = queries.get_pack(state['pack_id'])
    if pack_info['owner_id'] != user(update):
        update.message.reply_text(say.access_denied)
        return CHOOSE_PACK_ACTION
    update.message.reply_text(say.choose_pack_privacy, reply_markup=row_markup(PrivacyType.values()))
    return EDIT_PACK_PRIVACY


def edit_pack_privacy_h(bot, update):
    state = _states[user(update)]
    pack_info = queries.get_pack(state['pack_id'])
    text = update.message.text

    if pack_info['owner_id'] != user(update):
        update.message.reply_text(say.access_denied)
        return choose_pack_action(bot, update)
    if not PrivacyType.has(text):
        update.message.reply_text('Wrong privacy type')
        return edit_pack_privacy(bot, update)

    queries.update_pack_privacy(state['pack_id'], text)
    update.message.reply_text(say.pack_privacy_updated)
    return end(bot, update)


def edit_pack_status(bot, update):
    state = _states[user(update)]
    pack_info = queries.get_pack(state['pack_id'])
    update.message.reply_text(
        say.choose_pack_status,
        reply_markup=row_markup(CardStatusType.values())
    )
    return EDIT_PACK_STATUS


def edit_pack_status_h(bot, update):
    state = _states[user(update)]
    pack_info = queries.get_pack(state['pack_id'])
    text = update.message.text
    if not CardStatusType.has(text):
        update.message.reply_text('Wrong privacy type')
        return edit_pack_status(bot, update)
    queries.update_pack_status(user(update), state['pack_id'], text)
    update.message.reply_text(say.pack_status_updated)
    return end(bot, update)


def delete_pack(bot, update):
    state = _states[user(update)]
    pack_info = queries.get_pack(state['pack_id'])
    if pack_info['owner_id'] != user(update):
        update.message.reply_text(say.access_denied)
        return choose_pack_action(bot, update)
    update.message.reply_text(say.pack_deletion_confirmation_prompt.format(pack_info['name']))
    return DELETE_PACK


def delete_pack_h(bot, update):
    state = _states[user(update)]
    pack_info = queries.get_pack(state['pack_id'])

    if pack_info['owner_id'] != user(update):
        update.message.reply_text(say.access_denied)
        return choose_pack_action(bot, update)
    if update.message.text != say.pack_deletion_confirmation.format(pack_info['name']):
        update.message.reply_text('Cancelled deletion')
        return choose_pack_action(bot, update)

    queries.delete_pack(state['pack_id'])
    update.message.reply_text(say.pack_deleted)
    return choose_pack(bot, update)


def choose_card(bot, update):
    state = _states[user(update)]
    cards = queries.get_all_cards_in_pack(state['pack_id'])
    cards_print = ['{}: {} - {} - {}'.format(x['card_id'], x['front'],
                                             x['back'], x['comment'])
                   for x in cards]
    markup = [['Add card(s)', 'Export as file']] + \
             [[x] for x in cards_print]
    update.message.reply_text(
        '\n'.join(cards_print),
        reply_markup=ReplyKeyboardMarkup(markup, one_time_keyboard=True)
    )
    return CHOOSE_CARD


def choose_card_h(bot, update):
    update.message.reply_text(say.not_implemented)
    return choose_pack_action(bot, update)
