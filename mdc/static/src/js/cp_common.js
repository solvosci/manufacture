page_reload = function () {
    window.location.reload(true);
}

set_tare_zero = function () {

    $.ajax({
        url: '/mdc/cp/all/' + $('#chkpoint_id').val() + '/set_tare_zero',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({})
    }).done(function (data) {
        console.log(data.result);
        if ( data.result.err ) {
            show_info($('#t_scale_set_tare_zero_err').html() + ': ' + data.result.err, 'err');
        }
        else {
            show_info($('#t_scale_set_tare_zero_ok').html(), 'ok');
        }
    }).fail(function () {
        show_info($('#t_scale_set_tare_zero_err').html(), 'err');
    });

}

save_log = function (logdata) {

    $.ajax({
        url: '/mdc/cp/log',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(logdata)
    }).done(function (data) {
        // Does nothing
        console.log(data);
    }).fail(function () {
        // Does nothing
        console.log(data);
    });

}

show_info = function (message, level) {

    $('#info_div')
        .removeClass('info_div_ok info_div_err')
        .addClass('info_div_' + level)
        .html(message);

}

ws_create = function (onmessage_function, other_funcs) {

    // TODO uncomment this for testing purposes
    // return false;
    if ( $('#ws_simul').val().toLowerCase() === 'true' )  return;

    other_funcs = (other_funcs || {});

    var sessionId = $('#ws_session_id').val();
    var ws = new WebSocket($('#ws_wsapi_url').val());

    ws.onopen = function(){
        console.log('WebSocket opened');
        ws.send('bs-session-id' + "=" + sessionId);
        if ( other_funcs.onopen_function && (typeof other_funcs.onopen_function === 'function') ) {
            other_funcs.onopen_function();
        }
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

switch_enabled = function (obj, force_readonly) {
    if ( $(obj).hasClass('enabled') ) {
        $(obj).removeClass('enabled').addClass('disabled');
    }
    else {
        $(obj).removeClass('disabled').addClass('enabled');
    }
    $(obj).prop('disabled', force_readonly);
}

$(document).ready(function () {

    $('#reload_button').click(function () {
        page_reload();
    });
    $('#tare_zero_button').click(function () {
        set_tare_zero();
    });

});