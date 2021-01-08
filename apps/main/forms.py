class Bootstrap3FormMixin():
    """ 
        Adds the correct input classes for bootstrap 3 forms 
        Usage: class DerivedForm(Bootstrap3FormMixin, ModelForm): 
        (order matters)
    """
    def __init__(self, *args, **kwargs):
        super(Bootstrap3FormMixin, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.widget.input_type != 'checkbox':
                if field.widget.attrs.get('class'):
                    field.widget.attrs['class'] += ' form-control'
                else:
                    field.widget.attrs['class']='form-control'