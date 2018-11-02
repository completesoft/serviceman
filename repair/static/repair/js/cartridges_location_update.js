(function($) {

$(document).ready(function(){

    var table = $('#table').DataTable({
        "stateSave": true,
        "stateDuration": 0,
        "fnInitComplete": function(oSettings, json) {
                var cols = oSettings.aoPreSearchCols;
                for (var i = 0; i < cols.length; i++) {
                    var value = cols[i].sSearch;
                    if (value.length > 0) {
                        $("tfoot input")[i].value = value;
                    }
                }
        },
        "language": {
            "infoEmpty": "Показано с 0 по 0 из 0 записей",
            "lengthMenu": "Показать _MENU_ строк",
            "zeroRecords": "Нет данных удовлетворяющих условиям поиска",
            "search": "Поиск:",
            "info": "Показано с _START_ по _END_ из _TOTAL_ записей",
            "paginate": {
                "first":      "Первую",
                "last":       "Последняя",
                "next":       "Следующая",
                "previous":   "Предыдущая"
            },
        },
        "lengthMenu": [ [10, 25, 50, -1], [10, 25, 50, "ВСЕ"] ],
        'pageLength': 25,
        "columnDefs": [
            {
                'targets' : 1,
                render: function ( data, type, row, meta ) {
                    var dateSplit = data.split('.');
                    return type === "sort" ? dateSplit[2] +'-'+ dateSplit[1] +'-'+ dateSplit[0] : data;
                }
            }
        ]
   });


   table.columns().every( function () {
        var that = this;
        $( 'input', this.footer() ).on( 'keyup change', function () {
            if ( that.search() !== this.value ) {
                that.search( this.value ).draw();
            }
        });
   });


    $( "#table" ).on("dblclick", 'input.position', function(){$(this).prop('readonly', false);});
    $( "#table" ).on("focusout", 'input.position', function(){$(this).prop('readonly', true);});
    $("#table").on("click", "button.upd-location", get_cartridge);

});


function get_cartridge(event){

    var $input = $(this).closest('div').children('input');
    var input_text = $input.val()
    var $i = $(this).children('i');
    var csrf = getCookie('csrftoken');
    var url = window.location.href;
    var values = {'id': $(this).attr('cartridge'), 'client_position': $input.val()};

    var color = $i.css('color');
    update_anim($i, true);
    $.ajax({
            data: values,
            type: 'POST',
            url: url,
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrf);
                }
            },
            error: function() {
                $i.css('color', 'red');
                $input.prop('readonly', false);
                $input.val($input.prop('dump'));
                $input.prop('readonly', true);
                update_anim($i, false);
            },
            success: function(json, textStatus, request){
                if (json.status) {
                    $input.val(json.client_position);
                    $input.prop('dump', json.client_position);
                    $i.css('color', 'green');
                }
                else {
                    $i.css('color', 'red');
                    fader($input);
                    $input.val(input_text);
                }
                update_anim($i, false);
            },
            complete: function(){
                fader($input);
            }
    });
    return false;
}


function fader(jSelector){
    jSelector.fadeOut( "slow" , function(){jSelector.fadeIn( "slow" )});
}


function update_anim(jSelector, run=true){
    if (run){
        jSelector.addClass('fa-spin');
    }
    else{
        jSelector.removeClass('fa-spin');
    }
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