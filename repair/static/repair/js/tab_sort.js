$(document).ready(function(){
   var table = $('#table').DataTable({
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
});