/* jshint esversion: 6 */
"use strict";

// Hide/show narrative field based on tickbox
// Could be generalized through a register() function with a list of source elements and anonymous functions:
//    register_hide('id_rtw_type, [('id_rtw_document_type', (el) => el.checked)])
document.addEventListener("DOMContentLoaded", function() {
    const narrative_check = document.getElementById("id_custom_narrative");
    const hideable_group = document.getElementById("id_narrative").closest(".form-group");
    hideable_group.classList.add('hideable-input');

    function conditional_display() {
        hideable_group.classList.toggle('hidden', !narrative_check.checked);
    }
    narrative_check.onchange = conditional_display;

    // On page load
    conditional_display();
});
