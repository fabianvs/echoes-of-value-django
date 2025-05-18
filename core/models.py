from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from .utils import normalize

# --------------------------
# Core Character Model
# --------------------------
class Character(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    xp = models.IntegerField(default=0)
    energy = models.IntegerField(default=300)
    gold = models.IntegerField(default=500)
    level = models.IntegerField(default=1)
    is_npc = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return self.name

# --------------------------
# Character Stats
# --------------------------
class CharacterStats(models.Model):
    character = models.OneToOneField(Character, on_delete=models.CASCADE, related_name="stats")
    health = models.IntegerField(default=100)
    attack = models.IntegerField(default=10)
    defense = models.IntegerField(default=10)
    dexterity = models.IntegerField(default=10)
    intelligence = models.IntegerField(default=10)
    observation = models.IntegerField(default=10)

# --------------------------
# Item Metadata
# --------------------------
class Rarity(models.Model):
    name = models.CharField(max_length=50)
    color_code = models.CharField(max_length=7, help_text="Hex color code, e.g. #FFD700")

    def __str__(self):
        return self.name

class ItemType(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

# --------------------------
# Mission Metadata
# --------------------------
class MissionType(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

# --------------------------
# Inventory and Items
# --------------------------
class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    rarity = models.ForeignKey(Rarity, on_delete=models.SET_NULL, null=True)
    type = models.ForeignKey(ItemType, on_delete=models.SET_NULL, null=True)
    value = models.IntegerField(default=0)
    craftable = models.BooleanField(default=False)

class InventoryItem(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name="inventory")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

# --------------------------
# Crafting
# --------------------------
class Recipe(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    result = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="crafted_from")

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="ingredients")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField()

# --------------------------
# Exploration
# --------------------------
class Ruin(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    required_level = models.IntegerField(default=0)
    unlocked = models.BooleanField(default=False)

class Component(models.Model):
    name = models.CharField(max_length=100)
    ruin = models.ForeignKey(Ruin, on_delete=models.CASCADE, related_name="components")

# --------------------------
# Missions
# --------------------------
class Mission(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    type = models.ForeignKey(MissionType, on_delete=models.SET_NULL, null=True)
    reward_gold = models.IntegerField(default=0)
    reward_xp = models.IntegerField(default=0)
    reward_item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True)

class CharacterMission(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

    def current_step(self):
        return self.progress.filter(completed=False).order_by("step__order").first()

    def complete_step(self, step):
        progress = self.progress.filter(step=step).first()
        if progress and not progress.completed:
            progress.completed = True
            progress.save()
            EventLog.log(self.character, f"{self.character.name} completed the step '{step.description}' in mission '{self.mission.name}'")
            if step.success_response:
                EventLog.log(self.character, step.success_response)
            if not self.progress.filter(completed=False).exists():
                self.completed = True
                self.save()
                EventLog.log(self.character, f"{self.character.name} completed the mission '{self.mission.name}' 🎉")

class MissionStep(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name="steps")
    description = models.TextField()
    order = models.PositiveIntegerField()
    success_response = models.TextField(blank=True, help_text="Narrative response shown when this step is completed")

    class Meta:
        ordering = ['order']

class CharacterMissionProgress(models.Model):
    character_mission = models.ForeignKey(CharacterMission, on_delete=models.CASCADE, related_name="progress")
    step = models.ForeignKey(MissionStep, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

# --------------------------
# Marketplace
# --------------------------
class Auction(models.Model):
    seller = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='auctions')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class AuctionReputation(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    reputation = models.IntegerField(default=0)
    total_sales = models.IntegerField(default=0)
    total_earnings = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-reputation', '-total_earnings']

# --------------------------
# Social
# --------------------------
class Friendship(models.Model):
    from_character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='friends_sent')
    to_character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='friends_received')
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class CharacterReputation(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name="npc_reputations")
    npc = models.ForeignKey(Character, on_delete=models.CASCADE, related_name="reputation_from_players")
    reputation = models.IntegerField(default=0)

    class Meta:
        unique_together = ('character', 'npc')

# --------------------------
# MMO Text System
# --------------------------
class Zone(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    is_safe_zone = models.BooleanField(default=False)
    fallback_message = models.TextField(blank=True, help_text="Fallback response when a command fails in this zone")

    def __str__(self):
        return self.name

class CharacterLocation(models.Model):
    character = models.OneToOneField(Character, on_delete=models.CASCADE)
    zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True)
    last_moved = models.DateTimeField(auto_now=True)

class EventLog(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name="events")
    message = models.TextField()
    timestamp = models.DateTimeField(default=now)

    @classmethod
    def log(cls, character, message):
        return cls.objects.create(character=character, message=message)

class TextCommand(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    command = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        EventLog.log(self.character, f"{self.character.name} executed command: '{self.command}'")

        character_missions = CharacterMission.objects.filter(character=self.character, completed=False)
        matched = False
        for cm in character_missions:
            step = cm.current_step()
            if step and normalize(step.step.description) == normalize(self.command):
                cm.complete_step(step.step)
                matched = True
                break

        if not matched:
            location = getattr(self.character, "location", None)
            zone = getattr(location, "zone", None)
            fallback = zone.fallback_message if zone and zone.fallback_message else "Nothing happened... maybe try something else."
            EventLog.log(self.character, fallback)

# --------------------------
# Ruin Loot Table
# --------------------------
class RuinItemDrop(models.Model):
    ruin = models.ForeignKey(Ruin, on_delete=models.CASCADE, related_name="item_drops")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    drop_chance = models.FloatField(help_text="Chance from 0.0 to 1.0")

    class Meta:
        unique_together = ('ruin', 'item')

    def __str__(self):
        return f"{self.item.name} in {self.ruin.name} ({self.drop_chance * 100:.1f}% chance)"

