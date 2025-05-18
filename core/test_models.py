import unicodedata
import random
from django.test import TestCase
from django.contrib.auth.models import User
from core.models import (
    Character, CharacterStats, Rarity, ItemType, MissionType, Item, InventoryItem,
    Recipe, RecipeIngredient, Ruin, Component,
    Mission, MissionStep, CharacterMission, CharacterMissionProgress,
    Auction, Friendship, Zone, CharacterLocation, EventLog, TextCommand, RuinItemDrop
)
from core.utils import get_random_loot_for_ruin

def normalize(text):
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii").lower().strip()


class CharacterModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.character = Character.objects.create(user=self.user, name="Hero")

    def test_character_creation(self):
        self.assertEqual(self.character.name, "Hero")
        self.assertEqual(self.character.level, 1)

    def test_stats_auto_create(self):
        CharacterStats.objects.create(character=self.character)
        self.assertEqual(self.character.stats.health, 100)


class MissionProgressTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="player1")
        self.character = Character.objects.create(user=self.user, name="Adventurer")
        self.mtype = MissionType.objects.create(name="Daily")
        self.mission = Mission.objects.create(name="Tutorial", type=self.mtype, reward_gold=100, reward_xp=50)
        self.step1 = MissionStep.objects.create(mission=self.mission, description="go north", order=1)
        self.step2 = MissionStep.objects.create(mission=self.mission, description="explore ruin", order=2)
        self.char_mission = CharacterMission.objects.create(character=self.character, mission=self.mission)
        CharacterMissionProgress.objects.create(character_mission=self.char_mission, step=self.step1)
        CharacterMissionProgress.objects.create(character_mission=self.char_mission, step=self.step2)

    def test_current_step(self):
        step = self.char_mission.current_step()
        self.assertEqual(step.step.description, "go north")

    def test_complete_step(self):
        self.char_mission.complete_step(self.step1)
        self.assertTrue(self.char_mission.progress.get(step=self.step1).completed)
        logs = EventLog.objects.filter(character=self.character)
        self.assertTrue(logs.filter(message__icontains="completed the step").exists())


class TextCommandTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="textuser")
        self.character = Character.objects.create(user=self.user, name="Scribe")
        self.mtype = MissionType.objects.create(name="Daily")
        self.mission = Mission.objects.create(name="Learning", type=self.mtype)
        self.step = MissionStep.objects.create(mission=self.mission, description="léete el libro", order=1)
        self.char_mission = CharacterMission.objects.create(character=self.character, mission=self.mission)
        CharacterMissionProgress.objects.create(character_mission=self.char_mission, step=self.step)

    def test_text_command_triggers_step_completion_and_logs(self):
        TextCommand.objects.create(character=self.character, command="leete el libro")  # uses normalized comparison
        progress = CharacterMissionProgress.objects.get(character_mission=self.char_mission, step=self.step)
        self.assertTrue(progress.completed)

        command_log = EventLog.objects.filter(character=self.character, message__icontains="executed command").exists()
        mission_log = EventLog.objects.filter(character=self.character, message__icontains="completed the step").exists()
        self.assertTrue(command_log)
        self.assertTrue(mission_log)

    def test_command_does_not_match_wrong_input(self):
        # Should not complete with wrong command
        TextCommand.objects.create(character=self.character, command="run away")
        progress = CharacterMissionProgress.objects.get(character_mission=self.char_mission, step=self.step)
        self.assertFalse(progress.completed)


class RuinLootTest(TestCase):
    def setUp(self):
        self.ruin = Ruin.objects.create(name="Forgotten Cave", description="Dusty and old.")
        self.common_item = Item.objects.create(name="Rusty Sword", value=10)
        self.rare_item = Item.objects.create(name="Ancient Amulet", value=200)

        RuinItemDrop.objects.create(ruin=self.ruin, item=self.common_item, drop_chance=1.0)  # Always drops
        RuinItemDrop.objects.create(ruin=self.ruin, item=self.rare_item, drop_chance=0.0)    # Never drops

    def test_loot_drops_respect_chance(self):
        """Rusty Sword should always drop, Ancient Amulet should never drop"""
        results = [get_random_loot_for_ruin(self.ruin) for _ in range(10)]

        for loot in results:
            self.assertIn(self.common_item, loot)
            self.assertNotIn(self.rare_item, loot)

    def test_loot_drops_with_randomized_chance(self):
        """Test drop chance between 0.0 and 1.0 with mocked randomness (optional)"""
        drop = RuinItemDrop.objects.get(ruin=self.ruin, item=self.rare_item)
        drop.drop_chance = 1.0
        drop.save()
        loot = get_random_loot_for_ruin(self.ruin)
        self.assertIn(self.rare_item, loot)
