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


    $("#get_all").click(function(){
        addParam();
   });


   $('#table tr').dblclick(function() {
        var href = $(this).find("a").attr("href");
        if(href) {
            window.location = href;
        }
    });

});

function addParam(){
    window.location.search = '?all=Bingo';
}

})(jQuery);