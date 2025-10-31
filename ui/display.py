
import textwrap

class Display:
    def welcome(self):
        print("="*40)
        print("Welcome to Hangman!")
        print("Full version: categories, scoring, logs, ASCII-art.")
        print("="*40)

    def show_stats(self, stats: dict):
        gp = stats.get("games_played", 0)
        w = stats.get("wins", 0)
        l = stats.get("losses", 0)
        ts = stats.get("total_score", 0)
        wr = stats.get("win_rate", 0.0)
        avg = stats.get("average_score_per_game", 0.0)
        print("\n-- Current Statistics --")
        print(f"Games played: {gp}  Wins: {w}  Losses: {l}  Total score: {ts}")
        print(f"Win rate: {wr:.2f}%  Avg score/game: {avg:.2f}")
        print("-" * 30)

    def prompt_category(self, categories):
        print("\nChoose a category by typing its name (or press Enter for random from all):")
        print(", ".join(categories))
        print("Type 'quit' to exit.")
        cat = input("Category: ").strip()
        if cat == "":
            return None  
        if cat.lower() == "quit":
            return None
        
        for c in categories:
            if c.lower() == cat.lower():
                return c
        print("Category not recognized; selecting from all categories.")
        return None

    def new_word_info(self, category, length):
        cat_display = category if category else "All"
        print(f"\nNew word selected from '{cat_display}' (length {length})\n")

    def show_state(self, progress, guessed, attempts_left, ascii_art):
        print("\n" + ascii_art)
        print("Word: ", progress)
        print("Guessed letters:", ", ".join(guessed) if guessed else "-")
        print(f"Remaining attempts: {attempts_left}\n")

    def prompt_guess(self):
        print("Enter a letter (or type 'guess <word>' to guess full word, 'quit' to exit):")
        inp = input("> ").strip()
        if inp.lower() == "quit":
            confirm = input("Are you sure you want to quit this round? (y/n): ").strip().lower()
            if confirm == "y":
                return None
            return ""
        return inp

    def prompt_full_word(self):
        print("Type the full word you want to guess (or blank to cancel):")
        full = input("Full word: ").strip()
        if full == "":
            return None
        return full

    def win(self, word, score):
        print("\nCONGRATULATIONS — You win!")
        print(f"Word: {word}")
        print(f"Points earned this round: {score}\n")

    def lose(self, word):
        print("\nYou lost. The word was:", word)
        print("Points earned this round: 0\n")

    def play_again(self):
        ans = input("Play again? (y/n): ").strip().lower()
        return ans == "y"

    def say(self, msg):
        print(msg)
