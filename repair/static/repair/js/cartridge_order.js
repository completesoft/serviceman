(function($) {

$(document).ready(function(){

    $("#filter_cartridge_form").on("click", "#filter_cartridge_btn", {form : "#filter_cartridge_form", dest_select:'#id_cartridge'}, get_cartridge);

});

function get_cartridge(event){
    console.log(event.data)
    var form = $(event.data.form)
    var csrf = getCookie('csrftoken');
    var url = form.attr("action");
    var values = form.serializeArray();
    var destination = $(event.data.dest_select);

    console.log(values);
    $.ajax({
            data: values,
            type: form.attr("method"),
            url: url,
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrf);
                }
            },
            success: function(json, textStatus, request){
                console.log(json);
                console.log(textStatus);
                console.log(request);
                destination.empty();
                if (json.redirect) {
                    window.location.href = json.redirect+'?next='+window.location.pathname;
                }
                else {
                    $.each(json.cartridge, function(i, item) {
                        destination.append($('<option></option>').attr('value', item.id).text('Model:'+item.model+' S.n:'+item.serial_number+' Клиент:'+item.client__client_name));
                    });
                }
            }
    });
    return false;
}


function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = $.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}



})(jQuery);