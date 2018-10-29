(function($) {

$(document).ready(function(){

    $("#filter_cartridge_form").on("click", "#filter_cartridge_btn", {form : "#filter_cartridge_form", dest_select:'#id_cartridge'}, get_cartridge);
    $('#id_cartridge').on('change', {dest_field:'#id_client_position'}, change_position);

});

function change_position(event){
    val = ($('option:selected',this).attr('client_position')==null) ? '' : $('option:selected',this).attr('client_position');
    $(event.data.dest_field).attr('value', val);
}

function get_cartridge(event){
    var form = $(event.data.form)
    var csrf = getCookie('csrftoken');
    var url = form.attr("action");
    var values = form.serializeArray();
    var destination = $(event.data.dest_select);

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
                destination.empty();
                $('#id_cartridge').trigger('change');
                if (json.redirect) {
                    window.location.href = json.redirect+'?next='+window.location.pathname;
                }
                else {
                    $.each(json.cartridge, function(i, item) {
                        destination.append($('<option></option>').attr({value: item.id, client_position: item.client_position}).text('Model:'+item.model+' S.n:'+item.serial_number+' Клиент:'+item.client__client_name));
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