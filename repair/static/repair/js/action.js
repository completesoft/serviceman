
$(document).ready(function(){

    $("#add_spare").click(function() {
            addBlock("#spare_block", "#spare_div", "#id_spare-TOTAL_FORMS", "#id_spare-INITIAL_FORMS");
    });

    $("#add_service").click(function() {
    addBlock("#service_block", "#service_div", "#id_service-TOTAL_FORMS", "#id_service-INITIAL_FORMS");
    });

    $("#del_service").click(function() {
    delBlock("#service_block", "#service_div", "#id_service-TOTAL_FORMS", "#id_service-INITIAL_FORMS");
    });

    $("#del_spare").click(function() {
            delBlock("#spare_block", "#spare_div", "#id_spare-TOTAL_FORMS", "#id_spare-INITIAL_FORMS");
    });

    $("#add_dep").click(function() {
            addBlockShort("#dep_block");
    });

    $("#id_client_corp").click(function() {
            ableDep("#dep_block", "#add_dep");
    });

//    $("#ajax_client_add").attr("target","_blank");

});

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

function delBlock(source, destination, forms_counter, init_forms){

          var currentcount = parseInt($(forms_counter).val());
          var block = $(destination).children("fieldset:last");

          if(currentcount>1){
            $(block).remove();
            $(forms_counter).val(currentcount-1);
            $(init_forms).val(currentcount-1);
          }
}