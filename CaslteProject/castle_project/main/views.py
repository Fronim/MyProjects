from django.shortcuts import render
from django.core.serializers.json import DjangoJSONEncoder
import json
from .models import Researcher, Castle, PointOfInterest

def home_view(request):
    researcher = Researcher.objects.first()
    castle = Castle.objects.first()

    context = {
        'researcher': researcher,
        'castle': castle
    }
    return render(request, 'main/index.html', context)


def castle_3d_view(request):
    castle = Castle.objects.first()
    # Отримуємо всі точки для цього замку
    points = castle.points.all()

    # Формуємо список словників для JS
    points_data = list(points.values('title', 'description', 'position_x', 'position_y', 'position_z'))

    return render(request, 'main/castle_3d.html', {
        'castle': castle,
        'points_json': json.dumps(points_data, cls=DjangoJSONEncoder)
    })