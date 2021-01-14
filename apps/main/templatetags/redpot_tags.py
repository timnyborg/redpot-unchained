from django import template
from django.utils.safestring import mark_safe
import socket 

register = template.Library()

@register.simple_tag
def edit_button(url, icon='edit', target='', tooltip='Edit details'):
    """Converts a string into all lowercase"""
    b = f"""
        <a href="{url}"
           class="btn btn-default btn-lg pull-right"
           target="{target}"
           data=toggle': 'tooltip'
        ><span class='fas fa-{icon}'></span>
        </a>
    """
    return mark_safe(b)
    
@register.simple_tag
def timestamp(record):
    # This should be an inclusion tag
    
    created_on = record.created_on.strftime('%d %b %Y') if record.created_on else ''
    created_on_long = record.created_on.strftime('%Y-%m-%d %H:%M') if record.created_on else ''
    modified_on = record.modified_on.strftime('%d %b %Y') if record.modified_on else ''
    modified_on_long = record.modified_on.strftime('%Y-%m-%d %H:%M') if record.modified_on else ''
    
    return mark_safe(f"""    
        <div class="section-footer">
            <div class="timestamp">
                Created by { record.created_by}
                <span class="timeago" data-placement="bottom" data-title="{ created_on_long }" data-toggle="tooltip" datetime="2012-04-13 15:21">
                    { created_on }
                </span>
                <span class="separator">&bull;</span>
                Edited by { record.modified_by } 
                <span class="timeago" data-placement="bottom" data-title="{ modified_on_long }" data-toggle="tooltip" datetime="2020-12-15 17:16">
                    { modified_on }
                </span>
            </div>
        </div>
        """)
        
        
@register.inclusion_tag('utility/bootstrap3_form.html')
def bootstrap3form(form, status_classes=True):
    return {'form': form, 'status_classes': status_classes} 
    
    
@register.simple_tag
def bootstrap3submit(text='Submit', btn_type='primary', offset=2):
    return mark_safe(f"""
        <div class="form-group">    
            <div class="col-sm-offset-{offset} col-sm-{12-offset}">
                <button type="submit" class="btn btn-{btn_type}">{text}</button>
            </div>
        </div>
    """)
    
 
@register.simple_tag
def watermark(text=socket.gethostname()):
    return mark_safe(f"""
        <div id='watermark'>{(text + ' ')*150}</div>
    """)
