// Script to autohide long UL item lists
$('ul.hide-items').each(function(){
  var max = ($(this).data('max-item') - 1) || 1;
  var wrapper = "<div class='hide-wrapper'></div>";
  if ($(this).find(">li").length > max) {
    $(this)
      .find('>li:gt(' + max + ')')
      .wrapAll(wrapper)
      .parent()
      .hide()
      .parent('ul')
      .append(
        $('<li class="hide-toggle"><span class="rotate-icon fa fa-lg fa-chevron-down"></span></li>').click( function(){
            var wrapper = $(this).siblings('.hide-wrapper');
            var icon = $(this).children('.fa');
            icon.toggleClass('rotated');
            if (wrapper.hasClass('open')) {
                wrapper.slideUp(150);
            } else {
                wrapper.slideDown(300);
            }
            wrapper.toggleClass('open');
        })
    );
  }
});

// Load custom ckeditor configs
$('.ckeditor-custom').each(function() {
    CKEDITOR.replace($(this).attr('id'), {
        customConfig: '/redpot/static/js/ckeditor_config/' + $(this).data('ckeditor-config') + '.js?v=' + (new Date).getDay()
    });
});

// Add 'today' styling to any list items with created-on data for today
$('.item[data-created-on]').each(function() {
    var created = new Date($(this).data('created-on'));
    var today = new Date();

    if (created > today.setHours(0,0,0,0)) {
        $(this).addClass('today');
    }
});
