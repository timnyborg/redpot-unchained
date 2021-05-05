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
