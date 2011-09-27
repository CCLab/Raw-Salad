from django import forms

class FirstStepForm( forms.Form ):
    dataset = forms.CharField()
    view    = forms.CharField()
    issue   = forms.CharField( required=False )
    abbr    = forms.CharField( label="Smart abbrev" )
    desc    = forms.CharField( widget=forms.Textarea, label="Description" )
    file    = forms.FileField()
