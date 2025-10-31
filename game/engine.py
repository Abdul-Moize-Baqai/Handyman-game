
"""
Core gameplay logic. Implements GameEngine class that runs a single round and logs details.
"""
from pathlib import Path
from datetime import datetime
import json
import random
import string

class GameEngine:
    MAX_WRONG = 6

    def __init__(self, word: str, ascii_art, display, game_log_dir: Path, prev_stats: dict):
        self.word = word.lower()
        self.ascii_art = ascii_art
        self.display = display
        self.game_log_dir = game_log_dir
        self.prev_stats = prev_stats or {}
        self.guessed = set()
        self.wrong_guesses = []
        self.correct_guesses = []
        self.attempts_left = GameEngine.MAX_WRONG
        self.start_time = datetime.now()
        self.score_for_round = 0
        self.game_folder = None
        self.log_lines = []

        
        self._create_game_folder()

    def _create_game_folder(self):
        base = self.game_log_dir
        base.mkdir(parents=True, exist_ok=True)
        
        existing = [p.name for p in base.iterdir() if p.is_dir() and p.name.startswith("game")]
        nums = [int(''.join(filter(str.isdigit, n))) for n in existing if any(ch.isdigit() for ch in n)]
        next_num = (max(nums) + 1) if nums else 1
        self.game_folder = base / f"game{next_num}"
        self.game_folder.mkdir(parents=True, exist_ok=True)
        self.log_file = self.game_folder / "log.txt"

    def _record_guess(self, guess: str, correct: bool):
        """Record guess in order for logging"""
        t = len(self.log_lines) + 1
        status = "Correct" if correct else "Wrong"
        self.log_lines.append(f"{t}. {guess}  → {status}")

    def _write_log(self, result_text: str):
        data = [
            f"Game: {self.game_folder.name}",
            f"Category Source: (hidden during play)",
            f"Word: {self.word}",
            f"Word Length: {len(self.word)}",
            "",
            "Guesses (in order):",
        ]
        data.extend(self.log_lines)
        data.append("")
        data.append(f"Wrong Guesses List: {', '.join(self.wrong_guesses) if self.wrong_guesses else 'None'}")
        data.append(f"Wrong Guesses Count: {len(self.wrong_guesses)}")
        data.append(f"Remaining Attempts at End: {self.attempts_left}")
        data.append(f"Result: {result_text}")
        data.append(f"Points Earned: {self.score_for_round}")
        total_score = self.prev_stats.get("total_score", 0) + self.score_for_round
        data.append(f"Total Score (after this round): {total_score}")
        data.append("")
        games_played = self.prev_stats.get("games_played", 0) + 1
        wins = self.prev_stats.get("wins", 0)
        losses = self.prev_stats.get("losses", 0)
        if result_text.lower().startswith("win"):
            wins += 1
        else:
            losses += 1
        data.append(f"Games Played: {games_played}")
        data.append(f"Wins: {wins}")
        data.append(f"Losses: {losses}")
       
        win_rate = (wins / games_played) * 100 if games_played else 0.0
        data.append(f"Win Rate: {win_rate:.2f}%")
        data.append("")
        data.append(f"Date & Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        data.append("-" * 40)
        data.append("Session Notes:")
        data.append(f"- ASCII hangman final state index: {GameEngine.MAX_WRONG - self.attempts_left}")
        data.append(f"- Progress trace recorded in guesses above.")
        self.log_file.write_text("\n".join(data), encoding="utf-8")

    def _calculate_score(self, won: bool):
        """
        Scoring rules (clear and simple):
        - base = length_of_word * 10
        - bonus for remaining attempts: remaining_attempts * 5
        - penalty for wrong guesses: wrong_guesses_count * 8
        - losing yields 0
        """
        if not won:
            return 0
        base = len(self.word) * 10
        bonus = self.attempts_left * 5
        penalty = len(self.wrong_guesses) * 8
        score = max(base + bonus - penalty, 0)
        return score

    def _current_progress(self):
        return " ".join([c if c in self.guessed else "_" for c in self.word])

    def _is_word_revealed(self):
        return all(c in self.guessed for c in self.word)

    def play_round(self):
        """Main loop for a single round. Returns dict with results."""
        
        while True:
            self.display.show_state(progress=self._current_progress(),
                                    guessed=sorted(self.guessed | set(self.wrong_guesses)),
                                    attempts_left=self.attempts_left,
                                    ascii_art=self.ascii_art[GameEngine.MAX_WRONG - self.attempts_left])
            
            if self._is_word_revealed():
                self.score_for_round = self._calculate_score(won=True)
                self.display.win(self.word, self.score_for_round)
                self._write_log("Win")
                break
            if self.attempts_left <= 0:
                self.score_for_round = self._calculate_score(won=False)
                self.display.lose(self.word)
                self._write_log("Loss")
                break

            user_input = self.display.prompt_guess()
            if user_input is None:
                self._write_log("Quit")
                break

            user_input = user_input.strip().lower()
            if user_input == "":
                self.display.say("No input detected — please enter a letter or command.")
                continue

            if user_input.startswith("guess"):
                parts = user_input.split(maxsplit=1)
                if len(parts) == 1:
                    full = self.display.prompt_full_word()
                    if full is None:
                        self.display.say("Full-word guess cancelled.")
                        continue
                    full_guess = full.strip().lower()
                else:
                    full_guess = parts[1].strip().lower()

                if not full_guess.isalpha():
                    self.display.say("Full-word guess must be alphabetic.")
                    continue

                if full_guess == self.word:
                    self.guessed.update(set(self.word))
                    self._record_guess(full_guess, True)
                    self.display.say("Full-word guess correct!")
                else:
                    self.attempts_left -= 1
                    self.wrong_guesses.append(full_guess)
                    self._record_guess(full_guess, False)
                    self.display.say(f"Full-word guess '{full_guess}' is incorrect. -1 attempt.")
                continue

            if len(user_input) != 1 or not user_input.isalpha():
                self.display.say("Please input a single alphabetic character, or 'guess <word>' to guess the full word.")
                continue

            letter = user_input
            if letter in self.guessed or letter in self.wrong_guesses:
                self.display.say(f"You already guessed '{letter}'. No penalty.")
                continue

            if letter in self.word:
                self.guessed.add(letter)
                self.correct_guesses.append(letter)
                self._record_guess(letter, True)
                self.display.say("Correct!")
            else:
                self.attempts_left -= 1
                self.wrong_guesses.append(letter)
                self._record_guess(letter, False)
                self.display.say("Wrong!")

        return {
            "word": self.word,
            "score": self.score_for_round,
            "result": "Win" if self._is_word_revealed() else "Loss",
            "wrong_guesses": self.wrong_guesses,
            "timestamp": self.start_time.isoformat()
        }

    def update_and_get_stats(self):
        """
        Merge previous stats with this round's result and return the updated stats dict.
        Stats fields:
        games_played, wins, losses, total_score, win_rate, average_score_per_game
        """
        stats = dict(self.prev_stats) if self.prev_stats else {}
        stats.setdefault("games_played", 0)
        stats.setdefault("wins", 0)
        stats.setdefault("losses", 0)
        stats.setdefault("total_score", 0)

        stats["games_played"] += 1
        if self._is_word_revealed():
            stats["wins"] += 1
        else:
            stats["losses"] += 1
        stats["total_score"] += self.score_for_round
        stats["win_rate"] = (stats["wins"] / stats["games_played"]) * 100 if stats["games_played"] else 0
        stats["average_score_per_game"] = (stats["total_score"] / stats["games_played"]) if stats["games_played"] else 0
        return stats
