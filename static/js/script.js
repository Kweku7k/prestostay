
    $(function() {
        $("#city_query").autocomplete({
            source: function(request, response) {
                // Send an AJAX request to fetch city suggestions based on the user input.
                $.ajax({
                    url: "/autocomplete",
                    data: { term: request.term },
                    dataType: "json",
                    success: function(data) {
                        response(data);
                    }
                });
            }
        })
    });
