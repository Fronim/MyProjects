from django.contrib import admin
from .models import Researcher, Castle, ResearchWork, PointOfInterest

@admin.register(Researcher)
class ResearcherAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email')

# Це дозволить додавати точки прямо всередині сторінки Замку
class PointOfInterestInline(admin.StackedInline):
    model = PointOfInterest
    extra = 1 # Скільки пустих полів показувати за замовчуванням

@admin.register(Castle)
class CastleAdmin(admin.ModelAdmin):
    list_display = ('title',)
    inlines = [PointOfInterestInline] # <--- Підключаємо точки сюди

@admin.register(ResearchWork) # До речі, ти імпортував ResearchWork, але не зареєстрував його, виправимо це :)
class ResearchWorkAdmin(admin.ModelAdmin):
    list_display = ('title', 'publish_date')