/*jshint esversion: 6, strict: true */
/*global jQuery, $ */
//Handy decorator system for truncating tables.  Any table with class .hide-rows will have a 'More >' row appended, and hide everything
//  beyond 10 rows (provided there are 13+), or a number set by data-display (and optionally data-hide-after)

jQuery(function(){
    $('.hide-rows').each(function() {
        var rows = $(this).find('tr').length;
        var display = $(this).data('display') || 10;
        var hide_after = $(this).data('hide-after') || (display + 3);
        if (rows > hide_after) {
            $(this).append("<tr class='utility-row row-toggle hide-rows more'><td colspan='10'><b><a class='hide-rows'><span class='fa fa-chevron-down'></span> More</a></b></td></tr>"); //Placeholder
        }
    });

    $('a.hide-rows').click(function(event, duration) {
        //First 10 displayed, rest hidden, unless a data-display number is given
        var count = $(this).parents('table').data('display') || 10;
        var utilityrow = $(this).parents('tr');
        utilityrow.siblings().slice(count).toggle(typeof duration !== 'undefined' ? duration : 500);
        utilityrow.toggleClass('more less');

        if (utilityrow.hasClass('more')) {
            var inner = "<span class='fa fa-chevron-up'></span> Less";
        } else {
            var inner = "<span class='fa fa-chevron-down'></span> More";
        }
        $(this).html(inner); //Replace the link's content
    });

    //Default collapsed
    $('a.hide-rows').trigger('click', 0)
});

//Decorator for adding a 'new record' button to tables
//Uses the same utilityrow as above.  Creation and retrieval of the table's utility row could be abstracted from the .hide-rows bit
jQuery(function(){
    $('.add-record').each(function() {
        if ($(this).find('.utility-row').length > 0) {
            var utilityrow = $(this).find('.utility-row').first();
        } else {
            var utilityrow = $("<tr class='utility-row'><td colspan=10></tr></tr>");
            utilityrow.appendTo(this);
        }
        utilityrow.children('td').first().append("<a href=" + $(this).data('add-url') + "><span class='fa fa-plus'></span></a>"); //Placeholder
    });
});

//Add bs3 scheme to w2p error scheme
jQuery(function(){
    //$('.error').addClass('alert alert-danger');
});

jQuery(function(){
    $('#top-flash').hide().slideDown();
});

//Autogenerate sidenavs.  Any nav-anchor <a> will be added, with the following H3's title, overridable by giving the nav-anchor a data-title attr.
jQuery(function(){
    var linklist = $('#sidebar ul:first');
    if (linklist.length) {
        $('a.nav-anchor').each(function () {
            if ($(this).data('title')) {
                var title = $(this).data('title');
            } else {
                var title = $(this).next('h2').text();
            }
            var badge = '';
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

//Contextual action links for bs3 modals
$('.modal').on('show.bs.modal', function (event) {
    const button = $(event.relatedTarget); // Button that triggered the modal
    const target = button.data('href'); // Extract info from data-* attributes
    // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods
    const modal = $(this);
    modal.find('.modal-confirm-action').attr('formaction', target);
});

//jTruncate, adapted from http://www.jeremymartin.name/projects.php?project=jTruncate
//Modified to accept HTML in the more/less text, and put the more/less links inline
(function($){
    $.fn.jTruncate = function(options) {

        var defaults = {
            length: 300,
            minTrail: 20,
            moreText: '<small><span class="fa fa-chevron-right"></span></small>',
            lessText: '<small><span class="fa fa-chevron-left"></span></small>',
            ellipsisText: "... "
            //moreAni: "",
            //lessAni: ""
        };

        options = $.extend(defaults, options);

        return this.each(function() {
            var obj = $(this);
            var body = obj.html();

            if(body.length > options.length + options.minTrail) {
                var splitLocation = body.indexOf(' ', options.length);
                if(splitLocation != -1) {
                    // truncate tip
                    splitLocation = body.indexOf(' ', options.length);
                    var str1 = body.substring(0, splitLocation);
                    var str2 = body.substring(splitLocation, body.length - 1);
                    obj.html(str1 + '<span class="truncate_ellipsis">' + options.ellipsisText +
                        '</span>' + '<span class="truncate_more">' + str2 + '</span>');
                    obj.find('.truncate_more').css("display", "none");

                    // insert more link
                    obj.append('<a href="#" class="truncate_more_link">' + options.moreText + '</a>');

                    // set onclick event for more/less link
                    var moreLink = $('.truncate_more_link', obj);
                    var moreContent = $('.truncate_more', obj);
                    var ellipsis = $('.truncate_ellipsis', obj);
                    moreLink.click(function() {
                        if(moreLink.html() == options.moreText) {
                            moreContent.show();
                            moreLink.html(options.lessText);
                            ellipsis.css("display", "none");
                        } else {
                            moreContent.hide();
                            moreLink.html(options.moreText);
                            ellipsis.css("display", "inline");
                        }
                        return false;
                    });
                }
            } // end if

        });
    };
})(jQuery);

//Activate truncation of paragraphs
$('.truncate').jTruncate();

// A bottom right 'characters remaining' counter for textareas.  Give the textarea class=lengthcounter and data-max-length 255 or whatever
$(function() {
    $('.length-counter').after(function () {
        // Add the counter object
        return '<span class="length-counter-affix help-block pull-right"></span>';
    }).on('update_counter', function() {
        // Update counter object
        var text_remaining = $(this).data('max-length') - $(this).val().length;
        $(this).next('.length-counter-affix').html(text_remaining + ' remaining');
    }).keyup(function() {
        // Wire it up to keypresses
        $(this).trigger('update_counter');
    }).each(function() {
        // And initialize
        $(this).trigger('update_counter');
    });
});

// "Toggle all" checkboxes for datatables
$(function() {
    let select_all_box = document.getElementById('toggle-all');
    if (select_all_box){
        select_all_box.onclick = function () {
            // Get all other checkboxes
            let checkboxes = document.querySelectorAll("input[type='checkbox']:not([id*='toggle-all'])");
            for (let checkbox of checkboxes) {
                checkbox.checked = this.checked;
            }
        }
    }
})
