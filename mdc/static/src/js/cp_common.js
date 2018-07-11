show_info = function (message, level) {

    $('#info_div')
        .removeClass('info_div_ok info_div_err')
        .addClass('info_div_' + level)
        .html(message);

}

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