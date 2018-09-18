show_info = function (message, level) {

    $('#info_div')
        .removeClass('info_div_ok info_div_err')
        .addClass('info_div_' + level)
        .html(message);

}

ws_create = function (onmessage_function) {

    // TODO uncomment this for testing purposes
    // return false;

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

if (!String.prototype.format) {
  String.prototype.format = function() {
    var args = arguments;
    return this.replace(/{(\d+)}/g, function(match, number) {
      return typeof args[number] != 'undefined'
        ? args[number]
        : match
      ;
    });
  };
}

switch_enabled = function (obj) {
    if ( $(obj).hasClass('enabled') ) {
        $(obj).removeClass('enabled').addClass('disabled');
    }
    else {
        $(obj).removeClass('disabled').addClass('enabled');
    }
}