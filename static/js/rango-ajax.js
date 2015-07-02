// Ensure that whole document is loaded.
$(document).ready(function() {

    // Like button.
    $("#likes").click(function() {
        var catid;
        catid = $(this).attr("data-catid");
        $.get('/rango/like_category/', {
            category_id: catid
        }, function(data) {
            $("#like_count").html(data);
            $("#likes").hide();
        });
    });


    // Inline category search.
    $('#suggestion').keyup(function() {
        var query;
        query = $(this).val();
        $.get('/rango/suggest_category/', {
            suggestion: query
        }, function(data) {
            $("#cats").html(data);
        });
    });


    // Add page by the button near search suggestions.
    $(".btn-success").click(function() {
        var url;
        var title;
        var catid;
        url = $(this).attr("data-url")
        title = $(this).attr("data-title")
        catid = $(this).attr("data-catid")
        $.get('/rango/auto_add_page/', {
                url_data: url,
                title_data: title,
                catid_data: catid
            },
            function(data) {
                $("#page").html(data);
            });
    });

});