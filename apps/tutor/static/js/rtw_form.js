/* jshint esversion: 6 */
"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const elem = document.getElementById("id_rtw_type");
    const rtw_doc_div = document.getElementById("id_rtw_document_type").closest(".form-group");

    function slideDown(element) {
        element.style.opacity = 1;
        element.style.transition = "all 1s ease-in-out";

        if (element.classList.contains("has-error")) {
            // Should only occur on refresh
            element.style.height = "auto";
        } else {
            element.style.height = "54px";
        }
    }

    function slideUp(element) {
        element.style.opacity = 0;
        element.style.transition = "all 0.5s ease-in-out";
        element.style.height = "0px";
    }

    function rtw_div_display() {
        const rtw_check_by_div = document.getElementById("id_rtw_start_date").closest(".form-group");
        const rtw_doc_type_div = document.getElementById("id_rtw_end_date").closest(".form-group");

        if (elem.value === '1') {
            // List A
            slideDown(rtw_doc_div);
            slideUp(rtw_check_by_div);
            slideUp(rtw_doc_type_div);

        } else if (elem.value === '2') {
            // List B
            slideDown(rtw_doc_div);
            slideDown(rtw_check_by_div);
            slideDown(rtw_doc_type_div);
        } else {
            slideUp(rtw_doc_div);
            slideUp(rtw_check_by_div);
            slideUp(rtw_doc_type_div);
        }
    }

    // Dropdown change
    elem.onchange = rtw_div_display;

    // On page load
    rtw_div_display();
});
