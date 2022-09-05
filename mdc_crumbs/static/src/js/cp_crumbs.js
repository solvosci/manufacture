$(document).ready(function(){
    //Hide waiting websocket message
    show_info('', 'ok');
    //$("#info_div").css("color", "red");
    //$("#info_div").css("font-size", "1.5em");
    //$("#info_div").css("font-weight", "bold");
    
    //Select Employee
    $('#container_employees').on('click', 'div.bg-light', function() {
        if(!$("#weight_cleaning").attr("class").includes("disabled") && !$("#weight_nocleaning").attr("class").includes("disabled")){
            $("#selected").removeClass("bg-secondary text-white");
            $("#selected").addClass("bg-light");
            $('#selected').removeAttr('id');
            $(this).removeClass("bg-light");
            $(this).addClass("bg-secondary text-white");
            $(this).attr('id', 'selected');
        }
    });

    // Ajax to get lots
    loctactive_get = function () {
        old_lot = $("#lot_select").val()
        $.ajax({
            url: '/mdc/cp/crumbs/' + $('#chkpoint_id').val() + '/lotactive',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({})
        }).done(function (data) {
            data = JSON.parse(data.result)
            $('#lot_select').empty()
            $("#lot_select").append('<option value="" selected="selected">' + $("#t_chkpoint_crumbs_select_lot").text() + '</option>')
            for (var key in data) {
                if(!key.endsWith("code")){
                    if (data.hasOwnProperty(key)) {
                        $("#lot_select").append('<option value="' + key + '">' + data[key] + ' - ' + data[key + "code"] + '</option>')
                    }
                }
            }
            if ($('[value="' + old_lot + '"]').length > 0) {
                $("#lot_select").val(old_lot)
            }
            loctactive_get_schedule();
        }).fail(function () {
            show_info($('#t_chkpoint_win_lot_err_unknown').html(), 'err');
            loctactive_get_schedule();
        });
    
    }

    // Timer to get lots
    loctactive_get_schedule = function () {
        window.setTimeout(
            loctactive_get,
            5*1000
        );
    }

    // Get Employees
    $("#shift_select").on("change",function(){
        $(".card").remove()
        $.ajax({
            url: '/mdc/cp/crumbs/' + $('#chkpoint_id').val() + '/employee',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({"shift": $(this).val()})
        }).done(function (data) {
            data = JSON.parse(data.result)
            $("#container_employees div.card-title").remove();
            data.forEach(employee => {
                    $("#container_employees").append(
                        '<div class="card bg-light mb-3" value="' + employee[0] + "," + employee[2] + '" style="margin: 6px 15px; width: 250px; max-height: 70px;"><div class="card-body" style="padding: 0.4rem; overflow: hidden;"><h4 class="card-title text-wrap text-center">' + employee[1] + ' </h4></div></div>'
                    );
            });
        }).fail(function () {
            console.log("___err");
            show_info($('#t_chkpoint_crumbs_save_err_unknown').html(), 'err');
        });
    });

    // Button create record
    $("#weight_nocleaning").on("click",function(){
        if (!$("#weight_nocleaning").attr("class").includes("disabled")){
            if($("#selected").length == 1){
                $("#weight_nocleaning").addClass("disabled");
                $("#weight_cleaning").addClass("disabled");
                $("#shift_select").prop('disabled', true);
                $("#lot_select").prop('disabled', true);

                show_info('', 'ok');
                values = JSON.stringify({
                    'type': 'NotCleansed',
                    'shift': $("#shift_select").val(),
                    'employee': $("#selected").attr('value').split(",")[0],
                    'workstation': $("#selected").attr('value').split(",")[1],
                    'lot': $("#lot_select").val()
                })
                $.ajax({
                    url: '/mdc/cp/crumbs/' + $('#chkpoint_id').val() + '/createCrumb',
                    type: 'POST',
                    contentType: 'application/json',
                    data: values
                }).done(function (data) {
                    if (data.result){
                        if (data.result.created){
                            $("#last_weight").val(data.result.weight);
                            new_datetime = new Date().toLocaleString()
                            show_info($('#t_chkpoint_crumbs_save_unclean').html().format(new_datetime), 'ok');
                        }
                        else if(data.result.error){
                            show_info(data.result.error, 'err');
                        }
                        else{
                            show_info("Error inesperado", 'err');
                        }
                    }
                    else{
                        show_info(data.error.message, 'err');
                    }

                }).fail(function () {
                    show_info($('#t_chkpoint_crumbs_save_err_unknown').html(), 'err');
                }).always(function (){
                    $("#weight_nocleaning").removeClass("disabled");
                    $("#weight_cleaning").removeClass("disabled");
                    $("#shift_select").prop('disabled', false);
                    $("#lot_select").prop('disabled', false);
                    $("#selected").removeClass("bg-secondary text-white");
                    $("#selected").addClass("bg-light");
                    $('#selected').removeAttr('id');
                });
            }
            else {
                show_info($('#t_chkpoint_crumbs_err_employee_selection').html(), 'err');
            };
        }
    });

    // Button complete register
    $("#weight_cleaning").on("click",function(){
        if(!$("#weight_cleaning").attr("class").includes("disabled")){
            if($("#selected").length == 1){
                $("#weight_cleaning").addClass("disabled");
                $("#weight_nocleaning").addClass("disabled");
                $("#shift_select").prop('disabled', true);
                $("#lot_select").prop('disabled', true);
                show_info('', 'ok');
                values2 = JSON.stringify({
                    'type': 'Cleansed',
                    'shift': $("#shift_select").val(),
                    'employee': $("#selected").attr('value').split(",")[0],
                    'workstation': $("#selected").attr('value').split(",")[1],
                    'lot': $("#lot_select").val()
                    })
                $.ajax({
                    url: '/mdc/cp/crumbs/' + $('#chkpoint_id').val() + '/createCrumb',
                    type: 'POST',
                    contentType: 'application/json',
                    data: values2
                }).done(function (data) {
                    if(data.result.created){
                        $("#last_weight").val(data.result.weight);
                        new_datetime = new Date().toLocaleString()
                        show_info($('#t_chkpoint_crumbs_save_clean').html().format(new_datetime), 'ok');
                    }
                    else{
                        show_info(data.result.error, 'err');
                    }


                    
                }).fail(function () {
                    show_info($('#t_chkpoint_crumbs_save_err_unknown').html(), 'err');
                }).always(function (){
                    $("#weight_cleaning").removeClass("disabled");
                    $("#weight_nocleaning").removeClass("disabled");
                    $("#shift_select").prop('disabled', false);
                    $("#lot_select").prop('disabled', false);
                    $("#selected").removeClass("bg-secondary text-white");
                    $("#selected").addClass("bg-light");
                    $('#selected').removeAttr('id');
                });
            }
            else{
                show_info($('#t_chkpoint_crumbs_err_employee_selection').html(), 'err');
            }
        }
    });

    loctactive_get();

});
    