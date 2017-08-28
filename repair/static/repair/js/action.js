
$(document).ready(function(){

    $("#add_spare").click(function() {
            addBlock("#spare_block", "#spare_div", "#id_spare-TOTAL_FORMS", "#id_spare-INITIAL_FORMS");
          });

      $("#add_service").click(function() {
        addBlock("#service_block", "#service_div", "#id_service-TOTAL_FORMS", "#id_service-INITIAL_FORMS");
      });
});



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
          console.log("Before insert");
          $(destination).append(block);
          console.log("AFTER insert");

         }