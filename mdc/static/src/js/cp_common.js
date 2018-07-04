ws_create = function (onmessage_function) {

    var sessionId = $('#ws_session_id').val();
    var ws = new WebSocket($('#ws_wsapi_url').val());

    ws.onopen = function(){
        console.log('WebSocket opened');
        ws.send('bs-session-id' + "=" + sessionId);
    };

    ws.onmessage = onmessage_function;

    // TODO onerror

    return ws;

}