from ratings.models import Player, Team, Period, Match, Rating, Event, Alias, PreMatchGroup, PreMatch
from django.contrib import admin
from django.contrib.admin import DateFieldListFilter
from django.db.models import Q, F
from django import forms
from countries import transformations

def player_country(p):
    try:
        return transformations.cca_to_cn(p.country)
    except:
        return ''
player_country.short_description = 'Country'

class MembersInline(admin.TabularInline):
    model = Team.members.through

class AliasesInline(admin.TabularInline):
    model = Alias
    fields = ['name']

class PlayerAdmin(admin.ModelAdmin):
    fieldsets = [
            (None,          {'fields': ['tag','race']}),
            ('Optional',    {'fields': ['name','birthday','country']}),
            ('External',    {'fields': ['tlpd_kr_id','tlpd_in_id','lp_name','sc2c_id','sc2e_id']})
    ]
    inlines = [MembersInline, AliasesInline]
    search_fields = ['tag']
    list_display = ('tag', 'race', player_country, 'name')

class TeamAdmin(admin.ModelAdmin):
    fields = ['name', 'shortname', 'founded', 'disbanded', 'lp_name', 'homepage', 'active']
    inlines = [MembersInline, AliasesInline]
    search_fields = ['name']

def match_period(m):
    return str(m.period.id)
match_period.short_description = 'Period'

class MatchForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MatchForm, self).__init__(*args, **kwargs)
        q = Q(closed=False, lft=F('rgt')-1)
        if self.instance.eventobj != None:
            q = q | Q(id=self.instance.eventobj.id)
        self.fields['eventobj'].queryset = Event.objects.filter(q).order_by('-id')

class MatchAdmin(admin.ModelAdmin):
    list_display = ('date', 'get_res', match_period, 'treated', 'offline', 'game', 'eventobj', 'submitter')
    #list_filter = [('date', DateFieldListFilter)]
    form = MatchForm

    def get_res(self, obj):
        return '%s %i-%i %s' % (str(obj.pla), obj.sca, obj.scb, str(obj.plb))
    get_res.short_description = 'Result'

class EventAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'type', 'lft', 'rgt')
    exclude = ('lft', 'rgt')
    search_fields = ['fullname']

admin.site.register(Player, PlayerAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Match, MatchAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(PreMatchGroup)
admin.site.register(PreMatch)
