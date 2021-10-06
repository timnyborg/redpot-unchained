/*jshint esversion: 6 */
"use strict";

// Legacy row-hiding decorator
jQuery(function() {
    $('.hide-rows').each(function() {
        const rows = $(this).find('tr').length;
        const display = $(this).data('display') || 10;
        const hide_after = $(this).data('hide-after') || (display + 3);
        if (rows > hide_after) {
            $(this).append(
                `<tr class='hide-toggle open'><td colspan='100%'>
                    <span class="rotate-icon fas fa-lg fa-chevron-down"></span>
                </td></tr>`
            );
        }
    });
    const hide_row = $('tr.hide-toggle');
    hide_row.click(function(event, duration) {
        //First 10 displayed, rest hidden, unless a data-display number is given
        const count = $(this).parents('table').data('display') || 10;
        $(this).siblings().slice(count).toggle(typeof duration !== 'undefined' ? duration : 500);
        $(this).toggleClass('open');
    });

    //Default collapsed
    hide_row.trigger('click', 0);
});

//Autogenerate sidenavs.  Any nav-anchor <a> will be added, with the following H3's title, overridable by giving the nav-anchor a data-title attr.
// Legacy.  Replaced with function in tools for BS5
jQuery(function() {
    const linklist = $('#sidebar ul:first');
    if (linklist.length) {
        $('a.nav-anchor').each(function() {
            let title;
            if ($(this).data('title')) {
                title = $(this).data('title');
            } else {
                title = $(this).next('h2').text();
            }
            let badge = '';
            if ($(this).data('badge-text')) {
                if ($(this).data('badge-class')) {
                    badge = ' <span class="badge badge-' + $(this).data('badge-class') + '">' + $(this).data('badge-text') + '</span>';
                }
                else {
                    badge = ' <span class="badge">' + $(this).data('badge-text') + '</span>';
                }
            }
            linklist.append('<li><a href="#' + this.id + '"><span class="fa fa-chevron-left"></span>' + title + badge + '</a></li>');
        });

        $('body').scrollspy();
    }
});
