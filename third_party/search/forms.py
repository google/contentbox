from django import forms

class LiveSearchField(forms.CharField):
    def __init__(self, src, multiple_values=False, select_first=False,
                 auto_fill=False, must_match=False, match_contains=True,
                 placeholder='', **kwargs):
        attrs = {'src': src, 'placeholder': placeholder}
        classes = ['input-search']
        if multiple_values:
            classes.append('multiple-values')
        if select_first:
            classes.append('select-first')
        if auto_fill:
            classes.append('auto-fill')
        elif match_contains:
            classes.append('match-contains')
        if must_match:
            classes.append('must-match')
        if classes:
            attrs['class'] = ' '.join(classes)
        super(LiveSearchField, self).__init__(
            widget=forms.TextInput(attrs=attrs), **kwargs)
