(function($) {

$(document).ready(function(){
    $("#modal_reward_add").on("click", "#add_reward_button", function () {
      ajaxRewardAdd();
    });

    $("#reward_table").on("click", "button.delete", function () {
      ajaxRewardDel(this);
    });

    var table = $('#assessment_table').DataTable();

    table.columns().every( function () {
        var that = this;

        $( 'input', this.footer() ).on( 'keyup change', function () {
            if ( that.search() !== this.value ) {
                that
                    .search( this.value )
                    .draw();
            }
        } );
    } );

});


function ajaxRewardAdd(){
    var form = $("#reward_form");
    var csrf = getCookie('csrftoken');
    var values = $(form).serializeArray();
    values.push({name: "action", value: "add"});
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
                    $("#reward_panel").html(json.form);
                }
                else{
                    $("#reward_panel").html(json.form);
                    $("#reward_table > tbody:last").append(json.tr);
                }
            }
    });
    return false;
}

function ajaxRewardDel(button){
    var csrf = getCookie('csrftoken');
    var reward_id = $(button).attr("value");
    var url = $(button).attr("url");
    $.ajax({
            data: {"reward_id": reward_id, "action": "delete"},
            type: "POST",
            url: url,
            beforeSend: function(xhr, settings) {
                result = confirm("Вы действительно хотите удалить оплату?");
                if (!result){
                    return false;
                }
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrf);
                }
            },
            success: function(json){
                if (json.reward_id==reward_id)
                tr = $(button).parent().parent();
                $(tr).remove();
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