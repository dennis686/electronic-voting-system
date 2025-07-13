from django.contrib import admin
from .models import County, Constituency, Ward, Voter, Position, Candidate, Vote


@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Constituency)
class ConstituencyAdmin(admin.ModelAdmin):
    list_display = ['name', 'county']
    list_filter = ['county']
    search_fields = ['name']


@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ['name', 'constituency']
    list_filter = ['constituency']
    search_fields = ['name']


@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'id_number', 'email', 'county', 'constituency', 'ward', 'has_voted', 'is_verified']
    list_filter = ['county', 'constituency', 'ward', 'has_voted', 'is_verified']
    search_fields = ['full_name', 'id_number', 'email']


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_national']
    list_filter = ['is_national']
    search_fields = ['name']


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'county', 'constituency', 'ward']
    list_filter = ['position', 'county', 'constituency', 'ward']
    search_fields = ['name']

    def get_fields(self, request, obj=None):
        """
        Show only relevant fields based on whether position is national or not.
        """
        fields = ['name', 'position']
        if obj:
            if not obj.position.is_national:
                fields += ['county', 'constituency', 'ward']
        else:
            fields += ['county', 'constituency', 'ward']
        return fields

    def get_readonly_fields(self, request, obj=None):
        """
        Prevent editing of position field once candidate is created (optional).
        """
        if obj:
            return ['position']
        return []

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Add help text to regional fields to guide admin users.
        """
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'county':
            field.help_text = 'Select the county this candidate is contesting in.'
        elif db_field.name == 'constituency':
            field.help_text = 'Select the constituency if applicable.'
        elif db_field.name == 'ward':
            field.help_text = 'Select the ward for MCA-level positions.'
        return field


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['voter', 'candidate', 'timestamp']
    list_filter = ['candidate__position', 'timestamp']
    search_fields = ['voter__full_name', 'voter__id_number', 'candidate__name']
