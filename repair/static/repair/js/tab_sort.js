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

   var dateP = $('#id_period').daterangepicker({
       autoUpdateInput: false,
       "alwaysShowCalendars": true,
       ranges: {
        'Сегодня': [moment(), moment()],
        'Вчера': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
        'Последние 7 Дней': [moment().subtract(6, 'days'), moment()],
        'Последние 30 Дней': [moment().subtract(29, 'days'), moment()],
        'Текущий Месяц': [moment().startOf('month'), moment().endOf('month')],
        'Предыдущий Месяц': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
    },
    "locale": {
        "format": "DD/MM/YYYY",
        "separator": " - ",
        "applyLabel": "Применить",
        "cancelLabel": "Сбросить",
        "fromLabel": "С",
        "toLabel": "По",
        "customRangeLabel": "Пользовательский",
        "weekLabel": "W",
        "daysOfWeek": [
            "Вс",
            "Пн",
            "Вт",
            "Ср",
            "Чт",
            "Пт",
            "Сб"
        ],
        "monthNames": [
            "Январь",
            "Февраль",
            "Март",
            "Апрель",
            "Май",
            "Июнь",
            "Июль",
            "Август",
            "Сентябрь",
            "Октябрь",
            "Ноябрь",
            "Декабрь"
        ],
        "firstDay": 1
    },
    "opens": "left"
   });
//    document.getElementById('id_date_from').value = dateP.data('daterangepicker').startDate.get().format('DD.MM.YYYY');
//    document.getElementById('id_date_to').value = dateP.data('daterangepicker').endDate.get().format('DD.MM.YYYY');
   console.log(dateP.data('daterangepicker').endDate.get().format('DD.MM.YYYY'));

   dateRangeInit(document.getElementById('id_date_from'), document.getElementById('id_date_to'), dateP);


   dateP.on('apply.daterangepicker', function(ev, picker) {
    $(this).val(picker.startDate.format('DD.MM.YYYY') + ' - ' + picker.endDate.format('DD.MM.YYYY'));
    document.getElementById('id_date_from').value = picker.startDate.format('DD.MM.YYYY');
    document.getElementById('id_date_to').value = picker.endDate.format('DD.MM.YYYY');
   });

   dateP.on('cancel.daterangepicker', function(ev, picker) {
      $(this).val('----------');
      document.getElementById('id_date_from').value = '';
      document.getElementById('id_date_to').value = '';
   });

});

function addParam(){
    window.location.search = '?all=Bingo';
}

function dateRangeInit(date_from, date_to, picker){
    if(date_from && date_to){
        picker.data('daterangepicker').setStartDate(date_from.value);
        picker.data('daterangepicker').setEndDate(date_to.value);
        picker.value = date_from.value + ' - ' + date_to.value;
    }
}


})(jQuery);