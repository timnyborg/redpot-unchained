from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse

from django.template import Template, Context
from django.contrib import messages

from apps.programme.models import Programme, QA
from apps.programme.forms import ProgrammeForm

# Create your views here.



def view(request, programme_id):
    programme = Programme.objects.get(id=programme_id)
    modules = programme.modules.select_related('status').order_by('-start_date')[:200].all()
    module_count = programme.modules.count()
    students = QA.objects.filter(programme=programme.id).select_related('student').order_by('-start_date')[:200]


    return render(request, 'view.html', {'programme': programme, 'modules': modules, 'students': students, 'module_count': module_count, 'right_sidebar_enabled': True})

    
def edit(request, programme_id):
    programme = Programme.objects.get(id=programme_id)

    # Creating a form to add an article.
    # form = ArticleForm()

    # Creating a form to change an existing article.
    if request.method == "POST":
        form = ProgrammeForm(request.POST, instance=programme)
        if form.is_valid():
            form.save()
            messages.success(request, 'Details updated.')
            return redirect('programme:view', programme_id=programme.id)
    else:
        form = ProgrammeForm(instance=programme)
    
    return render(request, 'edit.html', {'form': form, 'programme': programme, 'right_sidebar_enabled': True})
    
    
from django.views.generic.edit import UpdateView
class Edit(UpdateView):    
    template_name = 'edit.html'
    form_class = ProgrammeForm
    model = Programme    

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        messages.success(self.request, 'Details updated.')
        return super().form_valid(form)
        
    def get_success_url(self):
        return reverse('programme:view', args=[self.object.id])