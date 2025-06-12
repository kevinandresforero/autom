import os
from src.bot_white_stones import BotWhiteStones

def center_text(text, width=60):
    return text.center(width)

def print_window_frame():
    width = 60
    print("╔" + "═" * (width - 2) + "╗")
    print("║" + " " * (width - 2) + "║")

def print_window_footer():
    width = 60
    print("║" + " " * (width - 2) + "║")
    print("╚" + "═" * (width - 2) + "╝")

def print_centered_lines(lines, width=60):
    for line in lines:
        print("║" + center_text(line, width - 2) + "║")

os.system('cls' if os.name == 'nt' else 'clear')

window_width = 60
welcome_lines = [
    "🤖 Welcome to DBO Bot! 🤖",
    "",
    "Hello! I am your assistant bot for DBOZero.",
    "",
    "With this bot, you can:",
    "1. Farm Whitestones automatically",
    "2. Use the Loot Assistant to help you",
    "   collect items and buff your character",
    "0. Configure the bot to your preferences",
    "",
]

print_window_frame()
print_centered_lines(welcome_lines, window_width)
print_window_footer()

# The options prompt is left-aligned for better readability
option = input(
    "Choose an option:\n"
    "1 - Farm Whitestones\n"
    "2 - Loot Assistant (includes buffing your character)\n"
    "0 - Configure\n"
    "> "
)

print_window_frame()
if option == "1":
    print_centered_lines([
        "You chose: Farm Whitestones"
    ], window_width)
    print_window_footer()
    bot = BotWhiteStones()
    bot.start()
    try:
        while True:
            pass  # Mantener el main activo
    except KeyboardInterrupt:
        print("Bot stopped.")
elif option == "2":
    print_centered_lines([
        "You chose: Loot Assistant (includes buffing your character)",
        "This feature is under construction."
    ], window_width)
    print_window_footer()
elif option == "0":
    print_centered_lines([
        "You chose: Configure",
        "This feature is under construction."
    ], window_width)
    print_window_footer()
else:
    print_centered_lines([
        "Invalid option"
    ], window_width)
    print_window_footer()