/*jshint esversion: 6 */
"use strict";

// Student marketing toggle
// Requires jquery instead of a DOMContentLoaded event because the toggle library uses jquery as well.
$(document).ready(function() {
    const email_arr = ["#id_email_optin_on", "#id_email_optin_method"];
    const mail_arr = ["#id_mail_optin_on", "#id_mail_optin_method"];

    function toggleFields(toggleItem, items) {
        // DOM ready
        if ($(toggleItem).parent().hasClass("off")) {
            items.forEach(item => $(item).closest('.form-group').slideUp(item));
        } else {
            items.forEach(item => $(item).closest('.form-group').slideDown(item));
        }
    }

    toggleFields('input#id_email_optin', email_arr);
    toggleFields('input#id_mail_optin', mail_arr);

    $('input#id_email_optin').change(function() {
        toggleFields('input#id_email_optin', email_arr);
    });

    $('input#id_mail_optin').change(function() {
        toggleFields('input#id_mail_optin', mail_arr);
    });
});
