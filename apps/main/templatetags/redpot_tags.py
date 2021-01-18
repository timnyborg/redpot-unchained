from django import template
from django.utils.safestring import mark_safe
import socket 

register = template.Library()


@register.simple_tag
def edit_button(url, icon='edit', target='', tooltip='Edit details'):
    """Produces a standard edit button"""
    b = f"""
        <a href="{url}"
           class="btn btn-default btn-lg pull-right"
           target="{target}"
           data-toggle': 'tooltip'
           title='{tooltip}'
        ><span class='fas fa-{icon}'></span>
        </a>
    """
    return mark_safe(b)

    
@register.simple_tag
def timestamp(record):
    # This should be an inclusion tag
    
    created_on = record.created_on.strftime('%d %b %Y %H:%M') if record.created_on else ''
    modified_on = record.modified_on.strftime('%d %b %Y %H:%M') if record.modified_on else ''

    return mark_safe(f"""    
        <div class="section-footer">
            <div class="timestamp">
                Created by { record.created_by}
                <span class="timeago" 
                    data-placement="bottom" 
                    data-title="{ created_on }" 
                    data-toggle="tooltip" 
                    datetime="{ created_on }"
                >
                    { created_on }
                </span>
                <span class="separator">&bull;</span>
                Edited by { record.modified_by } 
                <span class="timeago" 
                    data-placement="bottom" 
                    data-title="{ modified_on }" 
                    data-toggle="tooltip" 
                    datetime="{ modified_on }"
                >
                    { modified_on }
                </span>
            </div>
        </div>
        """)
        
        
@register.inclusion_tag('utility/bootstrap3_form.html')
def bootstrap3form(form, status_classes=True):
    return {'form': form, 'status_classes': status_classes} 


@register.inclusion_tag('utility/bootstrap3_modal.html')
def bootstrap3modal(modal_id, body, confirm_class='primary', confirm_text='Submit', cancel_text='Close', header='Confirm'):
    """Description from redpot: "A first stab at a terse modal generator".  Guess it stuck?"""
    return {
        'modal_id': modal_id,
        'body': body,
        'confirm_class': confirm_class,
        'confirm_text': confirm_text,
        'cancel_text': cancel_text,
        'header': header
    }


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
