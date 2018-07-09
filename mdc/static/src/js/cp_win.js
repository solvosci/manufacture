ws_event_received = function (event) {

    try {
        console.log('Event received:');
        console.log(event.data);

        var obj = JSON.parse(event.data);

        if ( !(obj.Event && obj.Event.device_id && obj.Event.user_id) ) {
            console.log('Event not recognized');
            return;
        }

        console.log('Device: ' + obj.Event.device_id.id);
        console.log('Card/User: ' + obj.Event.user_id.user_id);

        if ( $('#rfid_reader_code').val() === obj.Event.device_id.id ) {
            console.log('Matched!');
            $('#info_div')
                .removeClass('info_div_err').addClass('info_div_ok')
                .html('Read card #' + obj.Event.user_id.user_id);
            data_win_save({
                'card_code': obj.Event.user_id.user_id
            });
            return;
        }
        else {
            console.log('Skipped');
        }

    }
    catch (e) {
        $('#info_div')
            .removeClass('info_div_ok').addClass('info_div_err')
            .html('ERROR: ' + e.message);
    }

}

loctactive_get_schedule = function () {

    window.setTimeout(
        loctactive_get,
        5*1000
    );

}

loctactive_get = function () {

    $.ajax({
        url: '/mdc/cp/win/' + $('#chkpoint_id').val() + '/lotactive',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({})
    }).done(function (data) {
        console.log(data.result);
        if ( data.result.err ) {
            $('#info_div')
                .removeClass('info_div_ok').addClass('info_div_err')
                .html('ERROR retrieving active lot: ' + data.result.err);
            // TODO additional stuff over display
        }
        else {
            $('#lot').html(data.result.lotactive);
        }
        loctactive_get_schedule();
    }).fail(function () {
        $('#info_div')
            .removeClass('info_div_ok').addClass('info_div_err')
            .html('ERROR registering weight (unknown)');
        loctactive_get_schedule();
    });

}

data_win_save = function (data) {

    $.ajax({
        url: '/mdc/cp/win/' + $('#chkpoint_id').val() + '/save',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data)
    }).done(function (data) {
        console.log(data.result);
        if ( data.result.err ) {
            $('#info_div')
                .removeClass('info_div_ok').addClass('info_div_err')
                .html('ERROR ' + data.result.err);
            // TODO additional stuff over display
        }
        else {
            $('#info_div')
                .removeClass('info_div_err').addClass('info_div_ok')
                .html(
                    'Data successfully saved'
                );
            $('#lot').html(data.result.lotactive)
            $('#last_card_read').html(data.result.card_code)
            // TODO weight format
            $('#last_weight').html(data.result.weight + ' ' + data.result.w_uom)
            // TODO additional stuff over display
        }
    }).fail(function () {
        $('#info_div')
            .removeClass('info_div_ok').addClass('info_div_err')
            .html('ERROR registering weight (unknown)');
    });

}

$(document).ready(function() {

    /* var ws = */ws_create(ws_event_received);
    $('#info_div')
        .addClass('info_div_ok')
        .html('Ready for card readings!!!');

    loctactive_get();

});
