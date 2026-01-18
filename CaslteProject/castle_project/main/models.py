from django.db import models


class Researcher(models.Model):
    full_name = models.CharField(max_length=100, verbose_name="ПІБ")
    bio = models.TextField(verbose_name="Біографія")
    photo = models.ImageField(upload_to='researcher/', verbose_name="Фото", blank=True, null=True)
    bio_photo = models.ImageField(upload_to='researcher/', verbose_name="Фото для біографії", blank=True, null=True)
    email = models.EmailField(verbose_name="Email", blank=True, null=True)
    number = models.CharField(max_length=10)

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Дослідник"
        verbose_name_plural = "Дослідники"


class Castle(models.Model):
    title = models.CharField(max_length=200, verbose_name="Назва замку")
    description = models.TextField(verbose_name="Історична довідка / Опис")

    model_file = models.FileField(upload_to='3d_models/', verbose_name="Файл 3D моделі (.glb)")
    cover_image = models.ImageField(upload_to='castle_covers/', verbose_name="Обкладинка")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Замок"
        verbose_name_plural = "Замки"


class ResearchWork(models.Model):
    title = models.CharField(max_length=200, verbose_name="Назва роботи")
    summary = models.TextField(verbose_name="Короткий опис (анотація)")

    file = models.FileField(upload_to='documents/', verbose_name="Файл роботи (PDF)", blank=True, null=True)
    link = models.URLField(verbose_name="Посилання на публікацію", blank=True, null=True)

    publish_date = models.DateField(verbose_name="Дата публікації")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Наукова робота"
        verbose_name_plural = "Наукові роботи"


class PointOfInterest(models.Model):
    castle = models.ForeignKey(Castle, on_delete=models.CASCADE, related_name='points', verbose_name="Замок")
    title = models.CharField(max_length=200, verbose_name="Назва об'єкта")
    description = models.TextField(verbose_name="Опис")

    # Координати в 3D просторі (X, Y, Z)
    position_x = models.FloatField(verbose_name="Координата X")
    position_y = models.FloatField(verbose_name="Координата Y")
    position_z = models.FloatField(verbose_name="Координата Z")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Точка інтересу (POI)"
        verbose_name_plural = "Точки інтересу"