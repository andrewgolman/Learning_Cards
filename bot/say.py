from db import enums

access_denied = 'Access denied'

already_added = "You already have this pack in your list."

already_registered = "There is already an account for user with this TelegramID.\n"

begin_legend = "Now choose one of the suggested modes."

completed = "You have completed an exercise. If you've done it well - congrats:)"

choose_a_pack = "Choose a pack from a list below. Enter a number of a pack."

choose_general_goal = "Let's start with choosing a general goal for your learning." \
    "That will help me to suggest you entering different groups."

choose_learn_notifications = "I can remind you to look through your cards if you are off for a while." \
                             "Please, choose how often you wish to receive these notifications."

choose_mode = "Please, choose one of suggested modes. You can type /modes_help to find out more about them."

choose_pack = "Here is the list of your active packs. Choose one to show or edit. You can also create a /new_pack or /add_pack from our repository."

choose_pack_name = "Choose name for a new pack."

choose_pack_privacy = "Choose pack privacy level: it can be " + \
    ', '.join(enums.PrivacyType.values())

choose_pack_status = 'Choose pack status: it can be ' + \
    ', '.join(enums.CardStatusType.values())

choose_stats_notifications = "I can also tell you how much you've learned to give you some extra" \
                             "motivation. Now you can choose a way to get this kind of messages."

choose_type_of_review = "Choose type of review.\n" \
    "Trust - you will just tell me whether your last (mental) answer was right.\n" \
    "Enter - I'll ask you to type all the answers. No misprints!"

choose_username = "Our system will remember you by your TelegramID and nickname. First of all, choose the latter!"

choose_weekly_goal = "Your weekly goal is a number of cards to learn in a week. I recommend at least 50" \
                     "cards, but you may go for more! Enter a number to continue."

hello = "Hey, you're back! Time to make some progress, isn't it?"

help = "/menu - head menu\n" \
       "/begin - choose exercise\n" \
       "/packs - edit your packs and cards\n" \
       "/groups - see groups and import packs\n" \
       "/admin - administrate groups\n" \
       "" \
       "\n" \
       "Modes: available after choosing a pack\n" \
       "/review mode. Go through the pack and remember cards\n" \
       "/test mode\n" \
       "/learn mode - see the cards all together\n" \
       "/quit mode\n" \
       " \n" \
       "You can also \n" \
       "ask for /help \n" \
       "/cancel current action \n" \
       " \n" \
#  "/stats - "


incorrect_input = "Seems that you have enter something I hadn't expected. Please, read my previous" \
                  "instructions carefully, try again or type /help."

incorrect_weekly_goal = "Please, enter a positive integer not exceeding 1000."

invalid_pack = 'Pack file is invalid (line {})'

last_answer = "Your last answer was:"

learning_mode_legend = "Enter a number of a card to see the other side. You can /shuffle the cards," \
                    "/change_language or /quit."

menu_legend = "You are in the main menu. Choose a command from below list to begin."

no_packs_available = "No packs to show. You can add some with /new_pack or activate with /update."

no_groups_available = "No groups to show."

not_implemented = "Not implemented yet, stay tuned for updates."

not_recognized = "Your message wasn't recognized by bot\n" + \
    "Use /help for list of all commands"

pack_added = "Pack successfully added"

pack_created = 'Pack {} successfully created'

pack_deleted = 'Pack {} successfully deleted'

pack_deletion_confirmation = 'Yes, I want to delete pack {}'

pack_deletion_confirmation_prompt = 'Do you really want to DELETE this pack?\n' + \
    'It will be completely lost for you and any other users!\n' + \
    'If yes, repeat this phrase letter by letter:\n' + pack_deletion_confirmation + '\n' + \
    'Use /cancel or anything else to cancel'

pack_info = "Pack {}\nPrivacy: {}\nStatus: {}"

pack_is_empty = "Oops, there are no cards in this pack. You can add some using /edit."

pack_name_updated = 'Pack name was successfully changed'

pack_privacy_updated = 'Pack privacy was successfully changed'

pack_status_updated = 'Pack status was successfully changed'

registration_completed = "Congrats, you've completed the registration and are able to use all available functions."

right = "OK."

start_mode_learning = "start_mode_learning"

upload_pack_file = "Please send .cards file\n" \
    "It should contain cards as 'front side' - 'back side' - 'comment'\n" \
    "Last two parts are optional" \
    "File encoding must be UTF-8"

use_begin = 'Please, use /begin to practice this pack'

username_taken = "Oops. Our usernames are unique and this one seems to be taken. Please, try another one."

welcome = "Welcome to CardKeeper bot! ... Before you start, please, pass a quick registration procedure."


def choose_language(card):
    res = "Now choose language in which I'm going to ask you. I can't recognize languages yet, so let's count on an example."
    return str(res) + "\n" + "Front - as " + card.side[0] + "\n" + "Back - as " + card.side[1]


def enumerated(items):
    res = "Enter a number of a chosen option. \n"
    for i in enumerate(items):
        res = res + str(i[0] + 1) + ". " + i[1][1] + "\n"
    return res


def inter_results(a, b=None):
    s = "Your answer accuracy: \n"
    return s + str(a) + " / " + str(a+b)


def wrong(ans):
    return "Wrong. Right answer - " + ans + ".\n"
