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

        var device = $('#device_select').val();
        if ( device && (device == obj.Event.device_id.id) ) {
            console.log('Matched!');
            $('#card_read_input').val(obj.Event.user_id.user_id);
            $('#info_div').html('Read card #' + $('#card_read_input').val());
        }
        else {
            console.log('Skipped');
        }

    }
    catch (e) {
        $('#info_div').html('ERROR when reading card: ' + e.message);
    }

}

card_register_click = function () {

    try {
        if ( !$('#device_select').val() ) {
            throw new Error('there is no device selected');
        }
        if ( !$('#card_categ_select').val() ) {
            throw new Error('there is no card category selected');
        }
        if ( !$('#card_read_input').val() ) {
            throw new Error('first slide a card');
        }

        var data = {
            'card_code': parseInt($('#card_read_input').val()),
            'card_categ_id': parseInt($('#card_categ_select').val(), 10),
            'employee_id': parseInt($('#employee_select').val(), 10),
            'workstation_id': parseInt($('#workstation_select').val(), 10)
        }

        $('#info_div').html('Registering card... ');
        $.ajax({
            url: '/mdc/cp/cardreg/save',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data)
        }).done(function (data) {
            console.log(data.result);
            if ( data.result.err ) {
                $('#info_div').html('ERROR registering card: ' + data.result.err);
            }
            else {
                $('#info_div').html(
                    'Card #' + $('#card_read_input').val() + ' successfully registered with id ' + data.result.card_id
                );
                $('#card_read_input').val('');
            }
        }).fail(function () {
            $('#info_div').html('ERROR registering card');
        });
    }
    catch (e) {
        $('#info_div').html('ERROR registering card: ' + e.message);
    }

}

$(document).ready(function() {

    $('#confirm_button').click(card_register_click);

    // TODO error handling

    /* var ws = */ws_create(ws_event_received);
    $('#info_div').html('Ready for card registration!!!');

});