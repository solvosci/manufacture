/*$(document).ready(function () {
    ws = ws_get();
    ws.onmessage = function (event) {
        console.log(event);
        console.log(event.data);
        var obj = JSON.parse(event.data);
        console.log('Dispositivo: ' + obj.Event.device_id.id);
        console.log('Tarjeta/Usuario: ' + obj.Event.user_id.user_id);
    };
});*/

/*
var API_HOST = 'http://192.168.1.28',
    WS_HOST = 'ws://192.168.1.28',
    BIOSTAR2_LOGIN_API_URI = API_HOST + '/api/login',
    BIOSTAR2_WS_URI = WS_HOST + '/wsapi',
    BIOSTAR2_WS_EVENT_START_URI = API_HOST + '/api/events/start';
var retryNum = 1;

ws_event_start = function (bsSessionId) {

    console.log('Iniciando eventos con id. sesión ' + bsSessionId + '...');

    $.ajax({
        url: BIOSTAR2_WS_EVENT_START_URI,
        type: 'POST',
        dataType: 'json',
        contentType: 'application/json',
        headers: {'Access-Control-Allow-Origin': '*'},
        beforeSend: function(request) {
            request.setRequestHeader("bs-session-id", bsSessionId);
        },
        success: function(data, textStatus, request){
            console.log('Autentificación exitosa!');
            console.log(data, textStatus, request);
        },
        error: function(err){
            console.log('Error iniciando eventos:');
            console.log(err);
            if ( err.status == 500 ) {
                console.log('Autentificación aún pendiente, se procede al intento #' + ++retryNum);
                ws_event_start(bsSessionId);
            }
        }
    });

}

$(document).ready(function(){

    var loginData = {
        'User':{
            'login_id': 'admin',
            'password': 'SlvAtu$2018'
        }
    };

    $.ajax({
        url: BIOSTAR2_LOGIN_API_URI, // Biostar2 login api
        type: 'POST',
        dataType: 'json',
        data: JSON.stringify(loginData),
        contentType: 'application/json',
        headers: {'Access-Control-Allow-Origin': '*'},
        success: function(data, textStatus, request){
            var bsSessionId = request.getResponseHeader('bs-session-id'), // Biostar2 session id
                ws = new WebSocket(BIOSTAR2_WS_URI);

            ws.onopen = function(){
                console.log('WebSocket abierto');
                // If BioStar 2 session id is sent to 'bs-session-id' after WebSocket opens, you can get the event through onmessage.
                ws.send('bs-session-id' + "=" + request.getResponseHeader('bs-session-id'));
                ws_event_start(bsSessionId);
            };

            ws.onmessage = function (event) {
                console.log(event);
                console.log(event.data);
                var obj = JSON.parse(event.data);
                console.log('Dispositivo: ' + obj.Event.device_id.id);
                console.log('Tarjeta/Usuario: ' + obj.Event.user_id.user_id);
            };
        },
        error: function(err){
            console.log(err);
        },
    });

});
*/

$(document).ready(function() {
    var sessionId = $('#session_id').val();
    var ws = new WebSocket('ws://192.168.1.28/wsapi');

    ws.onopen = function(){
        console.log('WebSocket abierto');
        ws.send('bs-session-id' + "=" + sessionId);
    };

    ws.onmessage = function (event) {
        console.log(event);
        console.log(event.data);
        /* var obj = JSON.parse(event.data);
        console.log('Dispositivo: ' + obj.Event.device_id.id);
        console.log('Tarjeta/Usuario: ' + obj.Event.user_id.user_id); */
    };
});
