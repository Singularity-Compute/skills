"""Label content with several categories that can apply at once: one yes/no per label, not one choice."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from decide import decide

LABELS = {
    "spam": "Unsolicited advertising or repeated promotional content",
    "spoiler": "Reveals the ending or a major plot twist of a film, book or game",
    "question": "Asks the streamer or chat a genuine question",
    "insult": "Insults or mocks a person",
}
messages = [
    "lol the villain is actually her father, didn't see that coming",
    "BUY CHEAP COINS AT coins-4u dot com!!!",
    "what keyboard do you use?",
    "you play like my grandma, uninstall",
]
for m in messages:
    a = decide({"chat_message": m}, {label: {"type": "noul", "instructions": f"Is `chat_message` this: {desc}?"}
                                     for label, desc in LABELS.items()}, thinking="off")
    tags = [label for label in LABELS if a[label]["noul"] >= 0.5]
    print(f"{tags!s:24s} {m}")
