from django.contrib import admin
from .models import (
    Character, CharacterStats, Rarity, ItemType, Item, InventoryItem,
    Recipe, RecipeIngredient, Ruin, Component, RuinItemDrop,
    MissionType, Mission, MissionStep, CharacterMission, CharacterMissionProgress,
    Auction, AuctionReputation,
    Friendship, CharacterReputation,
    Zone, CharacterLocation,
    EventLog, TextCommand
)

class CharacterStatsInline(admin.StackedInline):
    model = CharacterStats
    can_delete = False

class InventoryItemInline(admin.TabularInline):
    model = InventoryItem
    extra = 0

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    inlines = [CharacterStatsInline, InventoryItemInline]
    list_display = ['name', 'is_npc', 'level', 'xp', 'energy', 'gold']
    list_filter = ['is_npc']
    search_fields = ['name', 'user__username']

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'rarity', 'value', 'craftable']
    list_filter = ['type', 'rarity']

@admin.register(RuinItemDrop)
class RuinItemDropAdmin(admin.ModelAdmin):
    list_display = ['ruin', 'item', 'drop_chance']
    list_filter = ['ruin']
    search_fields = ['item__name']

@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'reward_gold', 'reward_xp']
    search_fields = ['name']
    list_filter = ['type']

@admin.register(EventLog)
class EventLogAdmin(admin.ModelAdmin):
    list_display = ['character', 'message', 'timestamp']
    search_fields = ['character__name', 'message']
    list_filter = ['timestamp']

admin.site.register(CharacterStats)
admin.site.register(Rarity)
admin.site.register(ItemType)
admin.site.register(InventoryItem)
admin.site.register(Recipe)
admin.site.register(RecipeIngredient)
admin.site.register(Ruin)
admin.site.register(Component)
admin.site.register(MissionStep)
admin.site.register(CharacterMission)
admin.site.register(CharacterMissionProgress)
admin.site.register(Auction)
admin.site.register(AuctionReputation)
admin.site.register(Friendship)
admin.site.register(CharacterReputation)
admin.site.register(Zone)
admin.site.register(CharacterLocation)
admin.site.register(TextCommand)
admin.site.register(MissionType)