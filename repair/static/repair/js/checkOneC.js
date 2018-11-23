(function($) {

$(document).ready(function(){

    $('#CheckOneC').on('click', '#OneC', checkDoc);

    $('#copy').on('click', copyID);

});


function copyID(event){
  var orderId = document.getElementById('barcode');
  var range = document.createRange();
  range.selectNode(orderId);
  window.getSelection().addRange(range);
  try {
    document.execCommand('copy');
  } catch(err) {
    console.log('Can`t copy');
  }
  window.getSelection().removeAllRanges();
}

function checkDoc(event){
    var barcode = $("#barcode").text();
    var $oneCdocList = $('#insCheck');
    var $dest = $('#insCheck').find('div.modal-body').first();;
    var $i = $(this).children('i').first();

    var AjaxState = {
        objectChecked: 3,
        checked: function(){
            return this.objectChecked<=0;
        },
        markAction: function(){
            this.objectChecked--;
        },
        recordStr: function(view, str){
            this[view]+=str;
        },
        orderView: '',
        saleView: '',
        incomeView: ''
    };
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
          type: "GET",
          url: "http://192.168.168.110/cs-base/odata/standard.odata/Document_ЗаказПокупателя?$format=json&$filter=substringof('"+barcode+"',Комментарий) eq true",
          dataType: 'json',
          headers: {'Authorization': 'Basic ' + btoa('api:Q2w3E4r5')},
          beforeSend: function(xhr, settings) {
            $i.addClass('fa-spin');
          },
          success: function (data){
            AjaxState.markAction();
            if(data.value.length > 0){
                $.each( data.value, function( i, item ) {
                    AjaxState.recordStr('orderView', "<p class='bg-secondary'>"+"Заказ "+item.Date.slice(0,10)+" № "+item.Number+" : "+item.СуммаДокумента+" "+boolCheck(item.Posted)+"</p>");
                });
            }else{
                AjaxState.recordStr('orderView', "<p class='bg-secondary'>"+"Заказ ОТСУТСТВУЕТ"+"</p>");
            }
          },
          error: function(jqXHR, textStatus, errorThrown){
            AjaxState.markAction();
            AjaxState.recordStr('orderView', "<p class='bg-secondary'>"+"Нет соединения с сервером -"+textStatus+"</p>");
          },
          complete: function(jqXHR){
            if (AjaxState.checked()){
                $dest.append(AjaxState.orderView+AjaxState.saleView+AjaxState.incomeView);
                $i.removeClass('fa-spin');
                $oneCdocList.modal('show');
            }
          },
        });
    $.ajax
        ({
          type: "GET",
          url: "http://192.168.168.110/cs-base/odata/standard.odata/Document_РеализацияТоваровУслуг?$format=json&$filter=substringof('"+barcode+"',Комментарий) eq true",
          dataType: 'json',
          headers: {'Authorization': 'Basic ' + btoa('api:Q2w3E4r5')},
          success: function (data){
            AjaxState.markAction();
            if(data.value.length > 0){
                $.each( data.value, function( i, item ) {
                    AjaxState.recordStr('saleView', "<p class='bg-success'>"+"Реализация "+item.Date.slice(0,10)+" № "+item.Number+" : "+item.СуммаДокумента+" "+boolCheck(item.Posted)+"</p>");
                });
            }else{
               AjaxState.recordStr('saleView', "<p class='bg-success'>"+"Реализация ОТСУТСТВУЕТ"+"</p>");
            }
          },
          error: function(jqXHR, textStatus, errorThrown){
            AjaxState.markAction();
            AjaxState.recordStr('saleView', "<p class='bg-success'>"+"Нет соединения с сервером -"+textStatus+"</p>");
          },
          complete: function(jqXHR){
            if (AjaxState.checked()){
                $dest.append(AjaxState.orderView+AjaxState.saleView+AjaxState.incomeView);
                $i.removeClass('fa-spin');
                $oneCdocList.modal('show');
            }
          },
        });
    $.ajax
        ({
          type: "GET",
          url: "http://192.168.168.110/cs-base/odata/standard.odata/Document_ПоступлениеТоваровУслуг?$format=json&$filter=substringof('"+barcode+"',Комментарий) eq true",
          dataType: 'json',
          headers: {'Authorization': 'Basic ' + btoa('api:Q2w3E4r5')},
          success: function (data){
            AjaxState.markAction();
            if(data.value.length > 0){
                $.each( data.value, function( i, item ) {
                    AjaxState.recordStr('incomeView', "<p class='bg-info'>"+"Поступление "+item.Date.slice(0,10)+" № "+item.Number+" : "+item.СуммаДокумента+" "+boolCheck(item.Posted)+"</p>");
                });
            }else{
                AjaxState.recordStr('incomeView', "<p class='bg-info'>"+"Поступление ОТСУТСТВУЕТ"+"</p>");
            }
          },
          error: function(jqXHR, textStatus, errorThrown){
            AjaxState.markAction();
            AjaxState.recordStr('incomeView', "<p class='bg-info'>"+"Нет соединения с сервером -"+textStatus+"</p>");
          },
          complete: function(jqXHR){
            if (AjaxState.checked()){
                $dest.append(AjaxState.orderView+AjaxState.saleView+AjaxState.incomeView);
                $i.removeClass('fa-spin');
                $oneCdocList.modal('show');
            }
          },
        });
}

})(jQuery);