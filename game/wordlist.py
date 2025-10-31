
"""
Load words and provide random selection by category.
Also ensures there's at least `min_words` in words/words.txt by generating variants.
"""
from pathlib import Path
import random
import re

class WordList:
    def __init__(self, words_dir: Path):
        self.words_dir = words_dir
        self.words_file = self.words_dir / "words.txt"
        self.categories_dir = self.words_dir / "categories"
        self.categories_dir.mkdir(parents=True, exist_ok=True)

        
        self._ensure_default_categories()
        self._load_words()

    def _ensure_default_categories(self):
        """Create default category files if missing, with reasonable lists."""
        cat_samples = {
            "Animals.txt": [
                "lion","tiger","elephant","giraffe","dolphin","whale","zebra","kangaroo",
                "penguin","hedgehog","crocodile","alligator","ostrich","rhinoceros","hippopotamus",
                "panda","koala","fox","wolf","bear","camel","otter","badger","squirrel","rabbit",
                "platypus","seal","walrus","cheetah","leopard","monkey","gorilla","chimpanzee",
                "ant","bee","butterfly","snail","slug","lobster","crab","eel","octopus","squid",
                "shrimp","jellyfish","starfish","seal","mongoose","armadillo","mongoose"
            ],
            "Countries.txt": [
                "canada","brazil","argentina","india","china","france","germany","spain","portugal",
                "italy","japan","southkorea","northkorea","mexico","nigeria","egypt","kenya","ethiopia",
                "turkey","greece","sweden","norway","finland","denmark","poland","ukraine","belgium",
                "switzerland","australia","newzealand","thailand","vietnam","philippines","pakistan",
                "bangladesh","iran","iraq","saudiarabia","unitedstates","unitedkingdom"
            ],
            "Programming.txt": [
                "python","javascript","java","csharp","cpp","ruby","golang","rust","typescript",
                "swift","kotlin","php","perl","haskell","clojure","scala","matlab","bash","sql",
                "html","css","react","angular","vue","django","flask","spring","node","express",
                "tensorflow","pytorch","keras","numpy","pandas","docker","kubernetes","aws","azure"
            ],
            "Science.txt": [
                "physics","chemistry","biology","geology","astronomy","ecology","genetics","evolution",
                "microbiology","zoology","botany","quantum","relativity","thermodynamics","optics",
                "neuroscience","anatomy","physiology","biochemistry","meteorology","oceanography",
                "paleontology","immunology","virology","nanotechnology","astrophysics"
            ]
        }

        for fname, words in cat_samples.items():
            fpath = self.categories_dir / fname
            if not fpath.exists():
                fpath.write_text("\n".join(sorted(set(words))))

    def _load_words(self):
        """Load words into memory from words.txt and category files."""
        self.categories = {}
        
        for cat_file in self.categories_dir.glob("*.txt"):
            cat = cat_file.stem
            words = [w.strip().lower() for w in cat_file.read_text().splitlines() if w.strip()]
            words = [re.sub(r'[^a-z]', '', w) for w in words if re.sub(r'[^a-z]', '', w)]
            if words:
                self.categories[cat] = sorted(set(words))


        aggregated = set()
        for wlist in self.categories.values():
            aggregated.update(wlist)

        if self.words_file.exists():
            extra = [w.strip().lower() for w in self.words_file.read_text().splitlines() if w.strip()]
            extra = [re.sub(r'[^a-z]', '', w) for w in extra if re.sub(r'[^a-z]', '', w)]
            aggregated.update(extra)

        self.all_words = sorted(aggregated)
        self._persist_words_file()

    def _persist_words_file(self):
        self.words_file.write_text("\n".join(self.all_words))

    def available_categories(self):
        cats = sorted(self.categories.keys())
        return cats

    def get_random_word(self, category: str = None):
        """
        Return (word, source) where source indicates category or 'all'.
        """
        pool = []
        if category and category in self.categories:
            pool = self.categories[category]
            src = category
        else:
            pool = self.all_words
            src = "all"
        if not pool:
            raise RuntimeError("No words available in chosen pool.")
        word = random.choice(pool)
        return word.lower(), src

    def ensure_minimum_words(self, min_words=1000):
        """
        If words.txt currently has fewer than min_words, generate variants to reach min_words.
        This produces deterministic variations by appending suffixes to base words.
        """
        current = [w.strip() for w in self.words_file.read_text().splitlines() if w.strip()]
        current_set = set(current)
        if len(current_set) >= min_words:

            self.all_words = sorted(current_set)
            return

        base_words = sorted(set(current_set) or sum([v for v in self.categories.values()], []))
        if not base_words:
        
            base_words = ["hangman","python","programming","science","country","animal","computer","network"]

        i = 0
        suffix = 1
        while len(current_set) < min_words:
            for bw in base_words:
                candidate = f"{bw}{suffix}"
                
                cand_clean = ''.join(ch for ch in candidate if ch.isalpha())
                if cand_clean and cand_clean not in current_set:
                    current_set.add(cand_clean)
                if len(current_set) >= min_words:
                    break
            suffix += 1
            i += 1
            if i > 2000:
                break  
        
        self.words_file.write_text("\n".join(sorted(current_set)))
        self.all_words = sorted(current_set)
