ws_event_received = function (event) {

    console.log(event);
    console.log(event.data);
    /* var obj = JSON.parse(event.data);
    console.log('Dispositivo: ' + obj.Event.device_id.id);
    console.log('Tarjeta/Usuario: ' + obj.Event.user_id.user_id); */

}

$(document).ready(function() {

    /* var ws = */ws_create(ws_event_received);
    $('#info_div').html('Ready for card readings!!!');

});
