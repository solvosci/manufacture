// https://zer0.degree/chapter1/JavaScript-closure-and-design-patterns.html
var WoutState = /*(*/function () {

    var chkpoint_id = +$('#chkpoint_id').val();
    var card_categ_P_id = +$('#card_categ_P_id').val();
    var card_categ_L_id = +$('#card_categ_L_id').val();

    var cards_in = [];
    var card_workstation = null;
    var quality_id = +$('#quality_select').val();
    /* var last_weight = 0; */

    var info = function (message, level) {
        show_info(message, level);
        // TODO more suff?
    }

    var addCard = function (card_data) {
        // TODO validation stuff
        // 1.- Check card_categ
        console.log('Checking card category ' + card_data.card_categ_id + '...');
        // 2.- Check data saving

        if ( card_data.card_categ_id === card_categ_P_id ) {
            // Product card received
            if ( cards_in.length === 2 ) {
                // Too many product cards
                throw new Error(`Card #${card_data.card_code} not valid. Workstation card is expected`);
            }
            if ( !('win_weight' in card_data) ) {
                throw new Error(`Card #${card_data.card_code} not valid, there is no input associated!`);
            }
            // TODO check same associated lot
            // Product card is allowed
            cards_in.push(card_data);

            $('#card_in_' + cards_in.length).val('{0} {1}'.format(card_data.win_weight, card_data.win_uom));

            info(`Added product Card #${card_data.card_code}`, 'ok');
        }
        else if ( card_data.card_categ_id === card_categ_L_id ) {
            // Workstation card received
            if ( cards_in.length === 0 ) {
                // Workstation card is not allowed
                throw new Error(`Card #${card_data.card_code} not valid. Product card is expected`);
            }

            if ( !('workstation' in card_data) ) {
                throw new Error(`Card #${card_data.card_code} not valid, there is no workstation associated!`);
            }

            // Workstation card is allowed: fire saving data
            card_workstation = card_data;
            $('#card_workstation').val(card_data.workstation);
            console.log(`Added workstation Card #${card_data.card_code}. Saving...`)
            save();
            return;
        }
        else {
            throw new Error(`Card ${card_data.card_code} not valid`);
        }

    }

    var updateQuality = function () {
        quality_id = $('#quality_select').val();
    }

    var save = function () {

        $.ajax({
            url: '/mdc/cp/wout/' + chkpoint_id + '/save',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                cards_in: cards_in,
                card_workstation: card_workstation,
                quality_id: quality_id/*,
                wout_categ_id: ... */
            })
        }).done(function (data) {
            try {
                console.log(data.result);
                if ( data.result.err ) {
                    throw new Error('ERROR saving data: ' + data.result.err);
                }
                else {
                    displayUpdate(data.result);
                    reset();
                    return;
                }
            }
            catch (e) {
                info(e.message, 'err')
                // TODO additional stuff over display
            }
        }).fail(function () {
            info('ERROR saving data (unknown)', 'err');
        });

    }

    var displayUpdate = function (data) {
        $('#lot').html(data.lot);
        $('#card_in_1').val(cards_in[0].card_code).addClass('success');
        if ( cards_in.length > 1 ) {
            $('#card_in_2').val(cards_in[1].card_code).addClass('success');
        }
        $('#card_workstation').val(card_workstation.card_code).addClass('success');
        $('#last_weight').val(data.weight + ' ' + data.w_uom).addClass('success');
        info('Weight saved successfully', 'ok')
        window.setTimeout(function () {
                $('#card_in_1,#card_in_2,#card_workstation,#last_weight').removeClass('success');
            },
            3000
        );
    }

    var reset = function () {
        cards_in = [];
        card_workstation = null;
    }

    return {
        addCard: addCard,
        updateQuality: updateQuality
    }

}/*)()*/;

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
            read_card_manage(obj.Event.user_id.user_id);
        }
        else {
            console.log('Skipped');
        }

    }
    catch (e) {
        show_info('ERROR: ' + e.message, 'err');
    }

}

read_card_manage = function (card_code) {

    $.ajax({
        url: '/mdc/cp/carddata/' + card_code,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({})
    }).done(function (data) {
        try {
            console.log(data.result);
            if ( data.result.err ) {
                throw new Error('ERROR retrieving card data: ' + data.result.err);
            }
            else {
                woutState.addCard(data.result);
                return;
            }
        }
        catch (e) {
            show_info(e.message, 'err');
            // TODO additional stuff over display
        }
    }).fail(function () {
        show_info('ERROR retrieving card data (unknown)', 'err');
    });

}

var woutState = null;

$(document).ready(function() {

    /* var ws = */ws_create(ws_event_received);
    show_info('Ready for card readings!!!', 'ok');

    // TODO additional initial stuff

    woutState = WoutState();

    $('#quality_select')
        .change(woutState.updateQuality)
        .val($('#initial_quality_id').val())
        .change();

});
