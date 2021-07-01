# Common development patterns
This is a collection of solutions to common requirements

## "Create child" view
We often want to add a child record to an existing parent (e.g. adding an email to a student, adding a fee to a module), without requiring the user to _choose_ the parent from a giant list.

This can be accomplished by:

* Passing the parent's id as a URL argument
* Getting the parent object during `dispatch()`
* Adding it to the new child during `form_valid()`.  The child ModelForm doesn't need to know anything about the parent.

If you want to redirect back to the parent, you can use parent's `get_absolute_url()` in `get_success_url()`

Extra permissions checks could be added to `dispatch()`

=== "views.py"
    ```python
    class CreateFee(AutoTimestampMixin, CreateView):
        model = Fee
        form_class = forms.FeeForm
        ...

        def dispatch(self, request, *args, **kwargs):
            self.module = get_object_or_404(Module, pk=kwargs['parent_id'])
            return super().dispatch(request, *args, **kwargs)

        def form_valid(self, form):
            form.instance.module = self.module
            return super().form_valid(form)

        def get_success_url(self):
            return self.module.get_absolute_url() + '#fees'
    ```
=== "forms.py"
    ```python
    class FeeForm(ModelForm):
        class Meta:
            model = Fee
            fields = ('amount', ... )
    ```
=== "urls.py"
    ```python
    urlpatterns = [
        path('new/<int:parent_id>', views.CreateFee.as_view(), name='new'),
        ...
    ]
    ```

## "Attach" view (many-to-many)
Similarly, we often want to attach an object to another object: for this example,  connecting a module to a programme, creating a many-to-many record.  If the user has clicked 'add module' on the programme page, there's no need for them to choose the programme from a list.

This can be accomplished by:

* Passing the programme's id as a URL argument
* Getting the programme object during `dispatch()`
* Adding it to the form with `get_initial()`
* Setting the programme widget in the form to hidden and disabled (if not hidden,
  you may wind up with a _massive_ select input)
* The uniqueness error can be customized as below

This approach ensures that violating uniqueness on the many-to-many table results in a friendly form error, not a 500 IntegrityError.

=== "views.py"
    ```python
    class AddProgramme(LoginRequiredMixin, generic.CreateView):
        form_class = forms.AddProgrammeForm
        ...

        def dispatch(self, request, *args, **kwargs):
            self.module = get_object_or_404(Module, pk=kwargs['module_id'])
            return super().dispatch(request, *args, **kwargs)

        def get_initial(self):
            return {'module': self.module}

        def get_success_url(self):
            return self.module.get_absolute_url()
    ```

=== "forms.py"
    ```python
    class AddProgrammeForm(forms.ModelForm):
        module = forms.ModelChoiceField(
            queryset=models.Module.objects.all(),
            disabled=True,
            widget=forms.HiddenInput(),
        )

        class Meta:
            model = ProgrammeModule
            fields = ['programme', 'module']
            error_messages = {
                exceptions.NON_FIELD_ERRORS: {
                    'unique_together': 'The module is already attached to the programme'
                }
            }
    ```
=== "urls.py"
    ```python
    urlpatterns = [
        path('add-programme/<int:module_id>', views.AddProgramme.as_view(), name='add-programme'),
    ]
    ...
    ```
