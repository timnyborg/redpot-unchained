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

//Autogenerate sidenavs.  Any nav-anchor <a> will be added, with the following H3's title, overridable by giving the nav-anchor a data-title attr.
// Legacy.  Replaced with function in tools for BS5
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
