from django.db import models


class County(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Constituency(models.Model):
    name = models.CharField(max_length=100)
    county = models.ForeignKey(County, on_delete=models.CASCADE, related_name='constituencies')

    class Meta:
        unique_together = ('name', 'county')
        ordering = ['county__name', 'name']

    def __str__(self):
        return f"{self.name} - {self.county.name}"


class Ward(models.Model):
    name = models.CharField(max_length=100)
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE, related_name='wards')

    class Meta:
        unique_together = ('name', 'constituency')
        ordering = ['constituency__county__name', 'constituency__name', 'name']

    def __str__(self):
        return f"{self.name} - {self.constituency.name}"


class Voter(models.Model):
    full_name = models.CharField(max_length=100)
    id_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)

    has_voted = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, blank=True)
    constituency = models.ForeignKey(Constituency, on_delete=models.SET_NULL, null=True, blank=True)
    ward = models.ForeignKey(Ward, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.full_name} ({self.id_number})"


class Position(models.Model):
    name = models.CharField(max_length=100)
    is_national = models.BooleanField(default=False)  # True for President, etc.

    class Meta:
        ordering = ['-is_national', 'name']

    def __str__(self):
        scope = "National" if self.is_national else "Local"
        return f"{self.name} [{scope}]"


class Candidate(models.Model):
    name = models.CharField(max_length=100)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='candidates')

    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, blank=True)
    constituency = models.ForeignKey(Constituency, on_delete=models.SET_NULL, null=True, blank=True)
    ward = models.ForeignKey(Ward, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['position__is_national', 'position__name', 'name']

    def __str__(self):
        return f"{self.name} ({self.position.name})"


class Vote(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE, related_name='votes')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='votes')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('voter', 'candidate')
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.voter.full_name} → {self.candidate.name} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
