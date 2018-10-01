(function($) {

$(document).ready(function(){

    $("#modal_service_add").on("click", "#add_service_button", function () {
      ajaxServiceAdd();
    });

    $("#service_table").on("click", "button.delete", function () {
      ajaxServiceDel(this);
    });

    $("#modal_spare_add").on("click", "#add_spare_button", function () {
      ajaxSpareAdd();
    });

    $("#spare_table").on("click", "button.delete", function () {
      ajaxSpareDel(this);
    });

});

function ajaxSpareDel(button){
    var order_id = $(button).attr("order");
    var spare_id = $(button).attr("value");
    var url = $(button).attr("url");
    var csrf = getCookie('csrftoken');
    $.ajax({
            data: {"order_id": order_id, "spare_id": spare_id},
            type: "POST",
            url: url,
            beforeSend: function(xhr, settings) {
                result = confirm("Вы действительно хотите удалить эти расходные материалы?");
                if (!result){
                    return false;
                }
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrf);
                }
            },
            success: function(json){
                if (json.error) {
                    $(button).attr("title", json.error);
                }
                else{
                    tr = $(button).parent().parent();
                    $(tr).remove();
                }
            }
    });
    return false;
}


function ajaxSpareAdd(){
    var form = $("#spare_form");
    var csrf = getCookie('csrftoken');
    var values = $(form).serializeArray();
    $.ajax({
            data: values,
            type: form.attr("method"),
            url: form.attr("action"),
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrf);
                }
            },
            success: function(json){
                if (json.tr=="error") {
                    $("#spare_panel").html(json.form);
                }
                else{
                    $("#spare_panel").html(json.form);
                    $("#spare_table tbody").find("tr:last").before(json.tr);
                }
            }
    });
    return false;
}


function ajaxServiceDel(button){
    var order_id = $(button).attr("order");
    var service_id = $(button).attr("value");
    var url = $(button).attr("url");
    var csrf = getCookie('csrftoken');
    $.ajax({
            data: {"order_id": order_id, "service_id": service_id},
            type: "POST",
            url: url,
            beforeSend: function(xhr, settings) {
                result = confirm("Вы действительно хотите удалить эти работы?");
                if (!result){
                    return false;
                }
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrf);
                }
            },
            success: function(json){
                if (json.error) {
                    $(button).attr("title", json.error);
                }
                else{
                    tr = $(button).parent().parent();
                    $(tr).remove();
                }
            }
    });
    return false;
}


function ajaxServiceAdd(){
    var form = $("#service_form");
    var csrf = getCookie('csrftoken');
    var values = $(form).serializeArray();
    $.ajax({
            data: values,
            type: form.attr("method"),
            url: form.attr("action"),
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrf);
                }
            },
            success: function(json){
                if (json.tr=="error") {
                    $("#service_panel").html(json.form);
                }
                else{
                    $("#service_panel").html(json.form);
                    $("#service_table tbody").find("tr:last").before(json.tr);
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
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

})(jQuery);