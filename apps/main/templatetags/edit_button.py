from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def edit_button(url, icon='pencil', target='', tooltip='Edit details'):
    """Converts a string into all lowercase"""
    b = f"""
        <a href="{url}"
           class="btn btn-default btn-lg pull-right"
           target="{target}"
           data=toggle': 'tooltip'
        ><span class='fa fa-{icon}'></span>
        </a>
    """
    return mark_safe(b)
    
@register.simple_tag
def timestamp(record):
    # This should be an inclusion tag
    return mark_safe(f"""
    
    <div class="section-footer">
    <div class="timestamp">
        Created by {record.created_by}
        <span class="timeago" data-placement="bottom" data-title="13 Apr 2012 15:21" data-toggle="tooltip" datetime="2012-04-13 15:21">{ record.created_on.strftime('%d %b %Y') }</span><span class="separator">&bull;</span>Edited by { record.modified_by } <span class="timeago" data-placement="bottom" data-title="15 Dec 2020 17:16" data-toggle="tooltip" datetime="2020-12-15 17:16">{ record.modified_on.strftime('%d %b %Y') }</span></div></div>
    """)

@register.inclusion_tag('utility/bootstrap3_form.html')
def bootstrap3form(form):
    return({'form': form})
    
    

