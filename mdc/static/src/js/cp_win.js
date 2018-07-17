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
            show_info('Read card #' + obj.Event.user_id.user_id, 'ok');
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
        show_info('ERROR: ' + e.message, 'err');
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
            show_info('ERROR retrieving active lot: ' + data.result.err, 'err');
            // TODO additional stuff over display
        }
        else {
            $('#lot').html(data.result.lotactive);
        }
        loctactive_get_schedule();
    }).fail(function () {
        show_info('ERROR retrieving active lot (unknown)', 'err');
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
            show_info('ERROR: ' + data.result.err, 'err');
        }
        else {
            show_info('Data successfully saved', 'ok');
            $('#lot').html(data.result.lotactive)
            $('#last_card_read').val(data.result.card_code).addClass('success');
            $('#last_weight').val(data.result.weight + ' ' + data.result.w_uom).addClass('success');
            window.setTimeout(function () { $('#last_card_read,#last_weight').removeClass('success'); }, 3000);
        }
    }).fail(function () {
        show_info('ERROR registering weight (unknown)', 'err');
    });

}

$(document).ready(function() {

    /* var ws = */ws_create(ws_event_received);
    show_info('Ready for card readings!!!', 'ok');

    loctactive_get();

});
