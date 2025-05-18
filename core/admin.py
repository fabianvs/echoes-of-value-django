from django.contrib import admin
from .models import (
    Character,
    CharacterStats,
    Rarity,
    ItemType,
    MissionType,
    Item,
    InventoryItem,
    Recipe,
    RecipeIngredient,
    Ruin,
    Component,
    Mission,
    CharacterMission,
    MissionStep,
    CharacterMissionProgress,
    Auction,
    Friendship,
    RankingEntry,
    Zone,
    CharacterLocation,
    EventLog,
    TextCommand,
)

# Optional: inline models for convenience
class CharacterStatsInline(admin.StackedInline):
    model = CharacterStats
    can_delete = False

class InventoryItemInline(admin.TabularInline):
    model = InventoryItem
    extra = 0

class CharacterAdmin(admin.ModelAdmin):
    inlines = [CharacterStatsInline, InventoryItemInline]
    list_display = ['name', 'level', 'reputation', 'xp', 'energy', 'gold']
    search_fields = ['name', 'user__username']

class MissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'reward_gold', 'reward_xp']
    search_fields = ['name']
    list_filter = ['type']

class AuctionAdmin(admin.ModelAdmin):
    list_display = ['item', 'seller', 'price', 'created_at']
    search_fields = ['item__name', 'seller__name']

class EventLogAdmin(admin.ModelAdmin):
    list_display = ['character', 'message', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['character__name', 'message']

# Register all models
admin.site.register(Character, CharacterAdmin)
admin.site.register(CharacterStats)
admin.site.register(Rarity)
admin.site.register(ItemType)
admin.site.register(MissionType)
admin.site.register(Item)
admin.site.register(InventoryItem)
admin.site.register(Recipe)
admin.site.register(RecipeIngredient)
admin.site.register(Ruin)
admin.site.register(Component)
admin.site.register(Mission, MissionAdmin)
admin.site.register(CharacterMission)
admin.site.register(MissionStep)
admin.site.register(CharacterMissionProgress)
admin.site.register(Auction, AuctionAdmin)
admin.site.register(Friendship)
admin.site.register(RankingEntry)
admin.site.register(Zone)
admin.site.register(CharacterLocation)
admin.site.register(EventLog, EventLogAdmin)
admin.site.register(TextCommand)
