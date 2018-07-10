// https://zer0.degree/chapter1/JavaScript-closure-and-design-patterns.html
var WoutState = (function () {

    var cards_in = [];
    var card_workstation = null;
    /* var last_weight = 0; */

    var addCard = function (card_data) {
        // TODO validation stuff
        // 1.- Check card_categ
        console.log('Checking card category ' + card_data.card_categ_id + '...');
        // 2.- Check data saving

    }

    return {
        addCard: addCard
    }

})();

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

            read_card_manage(obj.Event.user_id.user_id);
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

read_card_manage = function (card_code) {

    $.ajax({
        url: '/mdc/cp/carddata/' + card_code,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({})
    }).done(function (data) {
        console.log(data.result);
        if ( data.result.err ) {
            $('#info_div')
                .removeClass('info_div_ok').addClass('info_div_err')
                .html('ERROR retrieving card data: ' + data.result.err);
            // TODO additional stuff over display
        }
        else {
            WoutState.addCard(data.result);
            return;
        }
    }).fail(function () {
        $('#info_div')
            .removeClass('info_div_ok').addClass('info_div_err')
            .html('ERROR retrieving card data (unknown)');
    });

}

$(document).ready(function() {

    /* var ws = */ws_create(ws_event_received);
    $('#info_div')
        .addClass('info_div_ok')
        .html('Ready for card readings!!!');

    // TODO additional initial stuff

    $('#quality_select').val(
        $('#initial_quality_id').val()
    );

});
