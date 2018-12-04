(function($) {

$(document).ready(function(){

    $("#qr").on('click', getQr)

});

function getQr(event){
    console.log(this);
    url = $(this).attr('url');
    window.open(url, "qr", "width=600,height=500");
}


})(jQuery);