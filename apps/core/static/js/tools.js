/*jshint esversion: 6, strict: true */


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

// Add 'today' styling to any list items with created-on data for today
$('.item[data-created-on]').each(function() {
    var created = new Date($(this).data('created-on'));
    var today = new Date();

    if (created > today.setHours(0,0,0,0)) {
        $(this).addClass('today');
    }
});

// Autogenerate BS5 sidenav
//Autogenerate sidenavs.  Any nav-anchor <a> will be added, with the following H3's title, overridable by giving the nav-anchor a data-title attr.
document.addEventListener('DOMContentLoaded', () => {
    let linklist = document.querySelector('#sidenav ul:first-child');
    if (linklist) {
        document.querySelectorAll('.section-title').forEach(function (anchor) {
            let title = anchor.dataset.title || anchor.innerText;
            let badge = '';
            if (anchor.dataset.badgeText) {
                let badge_class = anchor.dataset.badgeClass || 'bg-secondary';
                badge = `<span class="badge rounded-pill ${badge_class} ms-1">${anchor.dataset.badgeText}</span>`;
            }
            linklist.insertAdjacentHTML(
                'beforeend',
                `<a href="#${anchor.id}" class="list-group-item list-group-item-action">${title}${badge}</a>`
            );
        });
    }
});
