/* jshint esversion: 6 */
"use strict";

document.addEventListener("DOMContentLoaded", () => {
    // Payable is only enabled when visible is checked
    const is_visible = document.getElementById("id_is_visible");
    const is_payable = document.getElementById("id_is_payable");

    function web_fields_update() {
        is_payable.disabled = !is_visible.checked;
    }

    is_visible.onclick = function() {
        // Auto-check payable, for ease of data-entry
        is_payable.checked = this.checked;
        web_fields_update();
    };

    web_fields_update();
});
