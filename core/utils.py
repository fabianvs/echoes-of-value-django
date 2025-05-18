import unicodedata
import random

def normalize(text):
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii").lower().strip()

def get_random_loot_for_ruin(ruin):
    drops = []
    for drop in ruin.item_drops.all():
        if random.random() <= drop.drop_chance:
            drops.append(drop.item)
    return drops
