from django import forms

class FirstStepForm( forms.Form ):

    SEP_CHOICES = (
        ( ';', ';' ),
        ( ',', ',' ),
        ( '\t', 'TAB' ),
        ( ' ', 'SPACE' ),
    )

    dataset = forms.CharField()
    ds_desc = forms.CharField( widget=forms.Textarea, label="Dataset description" )
    view    = forms.CharField()
    vw_desc = forms.CharField( widget=forms.Textarea, label="Perspective description" )
    issue   = forms.CharField( required=False )
    abbr    = forms.CharField( label="Smart en-based abbrev" )
    delim   = forms.ChoiceField( choices=SEP_CHOICES, label="Delimiter" )
    file    = forms.FileField()
