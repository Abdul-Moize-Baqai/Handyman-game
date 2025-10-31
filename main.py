
from game.wordlist import WordList
from game.engine import GameEngine
from game.ascii_art import ASCII_ART
from ui.display import Display
from pathlib import Path
import json


def main():
    base_path = Path(__file__).parent
    words_dir = base_path / "words"
    game_log_dir = base_path / "game_log"

   
    words_dir.mkdir(parents=True, exist_ok=True)
    game_log_dir.mkdir(parents=True, exist_ok=True)

   
    wl = WordList(words_dir)
    wl.ensure_minimum_words(min_words=1000) 

    display = Display()
    display.welcome()

    stats_file = game_log_dir / "stats.json"
   
    if stats_file.exists():
        try:
            stats = json.loads(stats_file.read_text())
        except Exception:
            stats = {}
    else:
        stats = {}

    while True:
        display.show_stats(stats)
        category = display.prompt_category(wl.available_categories())
        if category is None:
            display.say("Goodbye — thanks for playing!")
            break

        word, src = wl.get_random_word(category)
        display.new_word_info(category, len(word))
        engine = GameEngine(word=word, ascii_art=ASCII_ART, display=display,
                            game_log_dir=game_log_dir, prev_stats=stats)
        result = engine.play_round()

       
        stats = engine.update_and_get_stats()
        stats_file.write_text(json.dumps(stats, indent=2))

        
        if not display.play_again():
            display.say("Thanks for playing — see you next time!")
            break

if __name__ == "__main__":
    main()
