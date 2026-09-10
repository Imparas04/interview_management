from django.db import models


class Department(models.Model):
    """
    A recruitment department (Python Development, Data Science, etc.).
    Kept deliberately simple - name + description - since departments
    are a lookup/reference table that JobRole and skill-matching logic
    will point to via ForeignKey later.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
