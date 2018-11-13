(function($) {

$(document).ready(function(){

    $('#CheckOneC').on('click', '#OneC', checkDoc);

});

function checkDoc(event){
    var result_text = '';
    var barcode = $("#barcode").text();
    var $dest = $(this).parent('div').next('div');
    var barcode = $("#barcode").text()
    $dest.empty();

    function boolCheck(bool) {
        if (bool){
            return "<span class='glyphicon glyphicon-ok'></span>";
        }else{
            return "<span class='glyphicon glyphicon-remove'></span>";
        }
    };

    $.ajax
        ({
          async: false,
          type: "GET",
          url: "http://192.168.168.110/cs-base/odata/standard.odata/Document_ЗаказПокупателя?$format=json&$filter=substringof('"+barcode+"',Комментарий) eq true",
          dataType: 'json',
          headers: {'Authorization': 'Basic ' + btoa('api:Q2w3E4r5')},
          success: function (data){
            if(data.value.length > 0){
                $.each( data.value, function( i, item ) {
                    result_text +="<p class='bg-secondary'>"+"Заказ "+item.Date.slice(0,10)+" № "+item.Number+" : "+item.СуммаДокумента+" "+boolCheck(item.Posted)+"</p>";
                });
            }else{
                result_text +="<p class='bg-secondary'>"+"Заказ ОТСУТСТВУЕТ"+"</p>";
            }
          },
          error: function(jqXHR, textStatus, errorThrown){
            result_text +="<p class='bg-secondary'>"+textStatus+" "+errorThrown+"</p>";
          },
          timeout: 3000
        });
    $.ajax
        ({
          async: false,
          type: "GET",
          url: "http://192.168.168.110/cs-base/odata/standard.odata/Document_РеализацияТоваровУслуг?$format=json&$filter=substringof('"+barcode+"',Комментарий) eq true",
          dataType: 'json',
          headers: {'Authorization': 'Basic ' + btoa('api:Q2w3E4r5')},
          success: function (data){
            if(data.value.length > 0){
                $.each( data.value, function( i, item ) {
                    result_text +="<p class='bg-success'>"+"Реализация "+item.Date.slice(0,10)+" № "+item.Number+" : "+item.СуммаДокумента+" "+boolCheck(item.Posted)+"</p>";
                });
            }else{
               result_text +="<p class='bg-success'>"+"Реализация ОТСУТСТВУЕТ"+"</p>";
            }
          },
          error: function(jqXHR, textStatus, errorThrown){
            result_text +="<p class='bg-success'>"+textStatus+" "+errorThrown+"</p>";
          },
          timeout: 3000
        });
    $.ajax
        ({
          async: false,
          type: "GET",
          url: "http://192.168.168.110/cs-base/odata/standard.odata/Document_ПоступлениеТоваровУслуг?$format=json&$filter=substringof('"+barcode+"',Комментарий) eq true",
          dataType: 'json',
          headers: {'Authorization': 'Basic ' + btoa('api:Q2w3E4r5')},
          success: function (data){
            if(data.value.length > 0){
                $.each( data.value, function( i, item ) {
                    result_text +="<p class='bg-info'>"+"Поступление "+item.Date.slice(0,10)+" № "+item.Number+" : "+item.СуммаДокумента+" "+boolCheck(item.Posted)+"</p>";
                });
            }else{
                result_text +="<p class='bg-info'>"+"Поступление ОТСУТСТВУЕТ"+"</p>";
            }
          },
          error: function(jqXHR, textStatus, errorThrown){
            result_text +="<p class='bg-info'>"+textStatus+" "+errorThrown+"</p>";
          },
          timeout: 3000
        });
    $dest.append(result_text);
}

})(jQuery);