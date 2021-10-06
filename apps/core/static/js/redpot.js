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
