(function($) {

$(document).ready(function(){

    $('#CheckOneC').on('click', '#OneC', checkDoc);

    $("#add_spare").click(function() {
            addBlock("#spare_block", "#spare_div", "#id_spare-TOTAL_FORMS", "#id_spare-INITIAL_FORMS");
    });

    $("#add_service").click(function() {
    addBlock("#service_block", "#service_div", "#id_service-TOTAL_FORMS", "#id_service-INITIAL_FORMS");
    });

    $("#add_dep").click(function() {
            addBlockShort("#dep_block");
    });

    $("#id_client_corp").click(function() {
            ableDep("#dep_block", "#add_dep");
    });

    $("#id_client").change(function() {
            ajaxUpdate("#id_client", "#id_client_dep");
    });

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
    var $dest = $('#insCheck').find('div.modal-body').first();
    var $i = $(this).children('i').first();
    var alterDest = $('#insCheck').find('div.modal-body').first()

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

function ajaxSpareDel(button){
    var order_id = $(button).attr("order");
    var spare_id = $(button).attr("value");
    var url = $(button).attr("url");
    $.ajax({
        data: {"order_id": order_id, "spare_id": spare_id},
        type: "GET",
        url: url,
        success: function(json){
            result = confirm("Вы действительно хотите удалить эти запчасти?");
            if (!result){
                return false;
            }
            $.ajax({
                    data: {"order_id": json.order_id, "spare_id": json.spare_id},
                    type: "POST",
                    url: url,
                    headers: { "X-CSRFToken": json.csrf_token },
                    success: function(json){
                        tr = $(button).parent().parent();
                        $(tr).remove();
                    }
            });
            return false;
        }
    });
    return false;
}


function ajaxSpareAdd(){
    var form = $("#spare_form");
    var csrf = $("#spare_form input[name=csrfmiddlewaretoken]").attr("value");
    $.ajax({
            headers: { "X-CSRFToken": csrf },
            data: form.serialize(),
            type: form.attr("method"),
            url: form.attr("action"),
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
    $.ajax({
            data: {"order_id": order_id, "service_id": service_id},
            type: "GET",
            url: url,
            success: function(json){
                result = confirm("Вы действительно хотите удалить эти работы?");
                if (!result){
                    return false;
                }
                $.ajax({
                        data: {"order_id": json.order_id, "service_id": json.service_id},
                        type: "POST",
                        url: url,
                        headers: { "X-CSRFToken": json.csrf_token },
                        success: function(json){
                            tr = $(button).parent().parent();
                            $(tr).remove();
                        }
                });
                return false;
            }
    });
    return false;
}


function ajaxServiceAdd(){
    var form = $("#service_form");
    var csrf = $("#service_form input[name=csrfmiddlewaretoken]").attr("value");
    $.ajax({
            headers: { "X-CSRFToken": csrf },
            data: form.serialize(),
            type: form.attr("method"),
            url: form.attr("action"),
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


function ajaxUpdate(source, destination){
    var csrf = $("[name=csrfmiddlewaretoken]").attr("value");
    request_url = '/repair/dep-update/' + $(source).val() + '/';
    var $destination = $(destination);
    $.ajax({
        url: request_url,
        type:'POST',
        headers: { "X-CSRFToken": csrf },
        success: function(json){
            $destination.empty();
            $.each(json, function(i, item) {
                $destination.append($('<option></option>').attr('value', item.id).text(item.client_dep_name));
            });
        }
    });
}


function ableDep(block, button){
    if ($("#id_client_corp").is(':checked') ) {
        $(block).removeClass("hidden");
        $(button).removeClass("hidden");
    }
    else {
        $(block).addClass("hidden");
        $(button).addClass("hidden");
    }
}


function addBlockShort(destination){
    var block = "<div class='alert alert-info alert-dismissable' id='dep_source'>\
              <button type='button' class='close' data-dismiss='alert' aria-hidden='true'>&times;</button>\
              <strong>Новое отделение:</strong><input type='text' class='form-control' name='client_dep_name'>\
          </div>";
    $(destination).append(block);
}


function addBlock(source, destination, forms_counter, init_forms){

          var currentcount = parseInt($(forms_counter).val());
          var block = $(source).clone();

          block.find("*").each(function(){
              var current_id = $(this).attr("id");
              var current_for = $(this).attr("for");
              var current_name = $(this).attr("name");

              if (current_id) {
                $(this).attr("id",  current_id.replace("0", currentcount));
                $(this).val("");
              }

              if (current_for) {
                $(this).attr("for", current_for.replace("0", currentcount));
              }

              if (current_name) {
                $(this).attr("name", current_name.replace("0", currentcount));
              }

          });

          $(forms_counter).val(currentcount+1);
          $(init_forms).val(currentcount+1);
          $(destination).append(block);
}

})(jQuery);