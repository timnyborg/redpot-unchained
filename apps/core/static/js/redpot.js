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

// Student marketing toggle
jQuery(function() {
    const email_arr =  ["#id_email_optin_on", "#id_email_optin_method"];
    const mail_arr =  ["#id_mail_optin_on", "#id_mail_optin_method"];

    function toggleFields (toggleItem, items) {
        // DOM ready
        if ($(toggleItem).parent().hasClass("off")) {
            items.forEach(item =>  $(item).closest('.form-group').slideUp(item));
        } else {
            items.forEach(item =>  $(item).closest('.form-group').slideDown(item));
        }
    }

    toggleFields('input#id_email_optin', email_arr)
    toggleFields('input#id_mail_optin', mail_arr)

    $('input#id_email_optin').change(function () {
        toggleFields('input#id_email_optin', email_arr)
    })

    $('input#id_mail_optin').change(function () {
        toggleFields('input#id_mail_optin', mail_arr)
    })
});
