/* jshint esversion: 6 */

// Script to autohide long UL item lists
$('ul.hide-items').each(function(){
  'use strict';
  let max = ($(this).data('max-item') - 1) || 1;
  let wrapper = "<div class='hide-wrapper'></div>";
  if ($(this).find(">li").length > max) {
    $(this)
      .find('>li:gt(' + max + ')')
      .wrapAll(wrapper)
      .parent()
      .hide()
      .parent('ul')
      .append(
        $('<li class="hide-toggle"><span class="rotate-icon fa fa-lg fa-chevron-down"></span></li>').click( function(){
            let wrapper = $(this).siblings('.hide-wrapper');
            let icon = $(this).children('.fa');
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
    'use strict';
    let created = new Date($(this).data('created-on'));
    let today = new Date();

    if (created > today.setHours(0,0,0,0)) {
        $(this).addClass('today');
    }
});

// Autogenerate BS5 sidenav
//Autogenerate sidenavs.  Any nav-anchor <a> will be added, with the following H3's title, overridable by giving the nav-anchor a data-title attr.
document.addEventListener('DOMContentLoaded', () => {
    'use strict';
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


// "Toggle all" checkboxes for datatables
document.addEventListener('DOMContentLoaded', () => {
    'use strict';
    let select_all_box = document.getElementById('toggle-all');
    if (select_all_box){
        select_all_box.onclick = function () {
            // Get all other checkboxes
            let checkboxes = document.querySelectorAll("input[type='checkbox']:not([id*='toggle-all'])");
            checkboxes.forEach(checkbox => checkbox.checked = this.checked);
        };
    }
});
