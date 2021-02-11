let saved_stations = [];
let current_station = "";
let selected_station_index = -1;
let radio_playing = false;
let volume_change_cb = {};

let saved_schedule = {
    "weekday_time" : "",
    "enabled_weekdays": [],
    "weekend_time": "",
    "enabled_weekend_days" : [],
    "next_alarm": ""
}

let socket = io();
socket.on('connect', function() {
    socket.emit('my event', {data: 'I\'m connected!'});
});

socket.on('station-status', function(msg) {
    console.log(msg);
    radio_playing = msg["playing"];
    current_station = msg["station_name"];
});

function get_stations(){
    return new Promise(function(resolve, reject){
        $.ajax("/get_stations").done(function(resp){
            resolve(resp);
        }).fail(function (jqXHR, textStatus, errorThrown){
            reject(errorThrown);
        })
    })
}

function update_playing(){
    if(radio_playing){
        $("#play-stop-button").html("<i class=\"fas fa-stop\"></i>");
        $("#playing-status").html("Playing:");
    } else{
        $("#play-stop-button").html("<i class=\"fas fa-play\"></i>");
        $("#playing-status").html("Stopped:");
    }
}

function update_volume(volume){
    if(volume < 0 || volume > 100){
        return;
    }
    let cmd = "/set_volume?volume=" + volume;
    $.ajax(cmd).done(function(resp) {
        if(resp !== "OK"){
            console.log(resp);
        }
    }).fail(function (jqXHR, textStatus, errorThrown){
        console.log(errorThrown);
    });
}

$("#play-stop-button").click(function(){
    let cmd = "";
    if(radio_playing){
        cmd = "/stop_radio";
    } else {
        cmd = "/start_radio";
    }
    console.log("Sending command: " + cmd);
    $.ajax(cmd).done(function(resp){
        console.log(resp);
        if(resp === "OK"){
            if(cmd === "/start_radio"){
                radio_playing = true;
            } else if (cmd === "/stop_radio"){
                radio_playing = false;
            }
            update_playing()
        } else {
            console.log(resp);
        }
    }).fail(function (jqXHR, textStatus, errorThrown){
        console.log(errorThrown);
    })
});

$("#day-all").click(function(){
    let checked = $("#day-all").prop("checked");
    if(checked){
        $("#day-monday").prop("checked", true);
        $("#day-tuesday").prop("checked", true);
        $("#day-wednesday").prop("checked", true);
        $("#day-thursday").prop("checked", true);
        $("#day-friday").prop("checked", true);
    } else{
        $("#day-monday").prop("checked", false);
        $("#day-tuesday").prop("checked", false);
        $("#day-wednesday").prop("checked", false);
        $("#day-thursday").prop("checked", false);
        $("#day-friday").prop("checked", false);
    }
})

function set_alarm_settings(){
    if(saved_schedule["enabled_weekdays"]["monday"]){
        $("#day-monday").prop("checked", true);
    }
    if(saved_schedule["enabled_weekdays"]["tuesday"]){
        $("#day-tuesday").prop("checked", true);
    }
    if(saved_schedule["enabled_weekdays"]["wednesday"]){
        $("#day-wednesday").prop("checked", true);
    }
    if(saved_schedule["enabled_weekdays"]["thursday"]){
        $("#day-thursday").prop("checked", true);
    }
    if(saved_schedule["enabled_weekdays"]["friday"]){
        $("#day-friday").prop("checked", true);
    }
    if(saved_schedule["enabled_weekend_days"]["saturday"]){
        $("#day-saturday").prop("checked", true);
    }
    if(saved_schedule["enabled_weekend_days"]["sunday"]){
        $("#day-sunday").prop("checked", true);
    }
    $("#next-alarm-time").html(saved_schedule["next_alarm"]);
}

function read_alarm_settings(){
    let weekday_all = $("day-all").prop("checked");
    let weekday_time = $("#weekday-time").val();
    let weekend_time = $("#weekend-time").val();
    let error_msg = "";
    let error = false;

    if(weekday_time === ""){
        error_msg += "Weekday time not set.";
        error = true;
    } else {
        saved_schedule["weekday_time"] = weekday_time;
    }

    if(weekend_time === ""){
        error_msg += "Weekend time not set.";
        error = true;
    } else {
        saved_schedule["weekend_time"] = weekend_time;
    }

    if(weekday_all){
        saved_schedule["enabled_weekdays"] = [
            "monday", "tuesday", "wednesday",
        "thursday", "friday"];
    } else{
        if($("#day-monday").prop("checked")){
            saved_schedule["enabled_weekdays"].push("monday");
        }
        if($("#day-tuesday").prop("checked")){
            saved_schedule["enabled_weekdays"].push("tuesday");
        }
        if($("#day-wednesday").prop("checked")){
            saved_schedule["enabled_weekdays"].push("wednesday");
        }
        if($("#day-thursday").prop("checked")){
            saved_schedule["enabled_weekdays"].push("thursday");
        }
        if($("#day-friday").prop("checked")){
            saved_schedule["enabled_weekdays"].push("friday");
        }
    }
    let weekend_all = $("#weekend-all").prop("checked");
    if(weekend_all){
        saved_schedule["enabled_weekend_days"] = ["saturday", "sunday"];
    } else {
        if($("#day-saturday").prop("checked")){
            saved_schedule["enabled_weekend_days"].push("saturday");
        }
        if($("#day-sunday").prop("checked")){
            saved_schedule["enabled_weekend_days"].push("sunday");
        }
    }
    if(error){
        $("#schedule-error-msg").html(error_msg);
        return false;
    } else {
        return true;
    }
}

function set_alarm_settings(){
    $("#weekday-time").val(saved_schedule["weekday_time"]);
    $("#weekend-time").val(saved_schedule["weekend_time"]);
    for(let i = 0; i < saved_schedule["enabled_weekdays"].length; i++){
        let day = saved_schedule["enabled_weekdays"][i];
        if(day === "monday"){
            $("#day-monday").prop("checked", true);
        }
        if(day === "tuesday"){
            $("#day-tuesday").prop("checked", true);
        }
        if(day === "wednesday"){
            $("#day-wednesday").prop("checked", true);
        }
        if(day === "thursday"){
            $("#day-thursday").prop("checked", true);
        }
        if(day === "friday"){
            $("#day-friday").prop("checked", true);
        }
    }
    for(let i = 0; i < saved_schedule["enabled_weekend_days"].length; i++){
        let day = saved_schedule["enabled_weekend_days"][i];
        if(day === "saturday"){
            $("#day-saturday").prop("checked", true);
        }
        if(day === "sunday"){
            $("#day-sunday").prop("checked", true);
        }
    }
}

/* Not needed?
function send_schedule(){
    return new Promise(function(resolve, reject){
        let schedule_b64 = btoa(JSON.stringify(saved_schedule));
        $.ajax("/save_schedule&schedule_b64=" + schedule_b64).done(function (resp){
            if(resp === "OK"){
                resolve(resp);
            } else {
                reject(resp);
            }
        })
    })
} */

function save_schedule(){
    console.log(saved_schedule);

    let sched_str = JSON.stringify(saved_schedule).replace(/\s/g, '');
    console.log(sched_str);
    let sched_b64 = btoa(sched_str);
    console.log(sched_b64);
    return new Promise(function(resolve, reject){
        $.ajax("/save_schedule?sched=" + sched_b64).done(function(resp){
            if(resp == "OK"){
                resolve(resp);
            } else{
                reject(resp);
            }
        })
    })
}

function get_schedule(){
    return new Promise(function(resolve, reject){
        $.ajax("/get_schedule").done(function(resp){
            console.log("Schedule b64:" + resp);
            let schedule_obj = {};
            try {
                schedule_obj = JSON.parse(atob(resp));
            } catch (e){
                console.log(e);
                throw e;
            }
            resolve(schedule_obj);
        })
    })
}

$("#alarm-save").click(function(){
    let success = read_alarm_settings();
    if(success){
        save_schedule().then(function(resp){
             console.log("Saved");
        });
    }

})

function update_stations(resp_json) {
    return new Promise(function (resolve, reject) {
        try {
            console.log(resp_json);
            saved_stations = JSON.parse(resp_json);
            resolve();
        } catch (e) {
            reject(e);
        }
    })
}

function update_current_station(resp_json){
    return new Promise(function (resolve, reject){
        try{
            current_station = JSON.parse(resp_json)[0];
            resolve()
        } catch (e){
            reject(e);
        }
    })
}

function set_current_station(station_url){
    return new Promise(function (resolve, reject) {
        $.ajax("/set_current_station?station_b64=" + btoa(station_url)).done(function(resp){
            if(resp == "OK"){
                resolve("OK");
            } else {
                reject(resp);
            }
        }).fail(function (jqXHR, textStatus, errorThrown){
            reject(errorThrown);
        })
    })
}

function get_current_station(){
    return new Promise(function(resolve, reject){
        $.ajax("/get_current_station").done(function(resp){
            if(resp.indexOf("ERR") < 0){
                resolve(resp);
            } else {
                reject(resp)
            }
        }).fail(function (jqXHR, textStatus, errorThrown){
            reject(errorThrown);
        })
    })
}

function render_stations(){
    let stationsHTML = "<div class='input-group'><ul class='list-group' id='station-list'>";
    for(let i = 0; i < saved_stations.length; i++){
        let checked = "";
        let active = "";
        let btn_class = "btn-outline-primary";
        if(current_station == saved_stations[i][0]){
            checked = "checked='checked'";
            active = "active";
            btn_class = "btn-outline-light";
        }
        stationsHTML += "<li id=\"saved-station-" + i + "\"class='list-group-item " + active + "'>" +
            "<!--<div class='input-group-prepend radio-btn-box inline-item'><div class='input-group-text'>-->" +
            "<input class='inline-item radio-btn-box' id=\"saved-station-" + i + "-radio\" type='radio' name='station-radio-btn' aria-label='Select this station as current' " + checked + "><!--</div></div>-->" +
            "<div class='station-info inline-item'><span class='station-name'>" + saved_stations[i][1] + "</span>\t:\t<span class='station-url'>" + saved_stations[i][0] + "</span></div>" +
            "<button type='button' class='btn " + btn_class + " edit-btn inline-item' id='edit-name-btn-" + i + "' data-toggle='modal' data-target='#edit-name-modal'>" +
            "<i class=\"fas fa-edit\"></i></button>"
            + "</li>";
    }
    stationsHTML += "</ul></div>";
    $("#saved-stations").html(stationsHTML);
    for(let i = 0; i < saved_stations.length; i++){
        // Set current station
        $("#saved-station-" + i + "-radio").click(function(){
            set_current_station(saved_stations[i][0]).then(function(){
                refresh_stations();
                for(let j = 0; j < saved_stations.length; j++){
                    if(j == i){
                        $("#saved-station-" + j).addClass("active");
                        $("#edit-name-btn-" + j).removeClass("btn-outline-primary");
                        $("#edit-name-btn-" + j).addClass("btn-outline-light");
                    } else {
                        $("#saved-station-" + j).removeClass("active");
                        $("#edit-name-btn-" + j).addClass("btn-outline-primary");
                        $("#edit-name-btn-" + j).removeClass("btn-outline-light");
                    }
                }

            });
            selected_station_index = i;
        });
        // Edit station name
        $("#edit-name-btn-" + i).click(function(){
            console.log("eh " + i);
            $("#station-name").html(saved_stations[i][1]);
            $("#station-url").html(saved_stations[i][0]);
            $("#new-station-name").val(saved_stations[i][1]);
            selected_station_index = i;
        })
    }
}

function update_saved_station_name(){
    let current_station_name = "";
    for(let i = 0; i < saved_stations.length; i++){
        if(saved_stations[i][0] == current_station){
            current_station_name = saved_stations[i][1];
        }
    }
    $("#selected-station-name").html(current_station_name);
}

function refresh_stations() {
    get_stations().then(function (resp) {
        get_current_station().then(function(resp2){
            update_current_station(resp2).then(function(){
                update_stations(resp).then(function () {
                    console.log("Success!");
                    render_stations();
                    update_saved_station_name();
                })
            })
        })
    })
}

$(document).ready(function(){
    refresh_stations();
    get_schedule().then(function (resp){
        console.log("Saved schedule: " + resp);
        if(resp !== null) {
            saved_schedule = resp;
            set_alarm_settings();
        }

    }).catch(function(e){
        console.log(e);
    })
    console.log("Loaded.");
});

function send_station(station_url){
    return new Promise(function(resolve, reject){
        let station_b64 = btoa(station_url);
        $.ajax("/add_station?station_b64=" + station_b64).done(function(resp){
            if(resp == "OK"){
                resolve();
            } else {
                reject(resp);
            }
        }).fail(function (jqXHR, textStatus, errorThrown){
            reject(errorThrown);
        })
    })
}

function update_station_name(station_url, new_name){
    return new Promise(function(resolve, reject){
        let station_b64 = btoa(station_url);
        let station_name_b64 = btoa(new_name);
        $.ajax("/update_station_name?station_b64=" + station_b64 +"&station_name_b64=" + station_name_b64).done(function(resp){
            if (resp == "OK"){
                resolve(resp);
            } else {
                reject(resp);
            }
        }).fail(function (jqXHR, textStatus, errorThrown){
            reject(errorThrown);
        })
    })
}

$("#add-station-btn").click(function(){
    let new_station_url = $("#new-station-url").val();
    console.log("Form value: " + new_station_url);
    let verified_url = "";
    try {
        verified_url = new URL(new_station_url);
    } catch(e){
        console.log("Error: " + e.message);
        $("#url-error-msg").show();
        $("#url-error-msg").html(e.message);
    } finally {
        if(verified_url != ""){
            console.log(new_station_url);
            $("#url-error-msg").hide();
            send_station(new_station_url).then(function(resp){
                //saved_stations.push(new_station_url);
                refresh_stations()
            });
        }
    }
    
    console.log("Station URL: " + verified_url);
});

$("#set-name-btn").click(function () {
    let new_station_name = $("#new-station-name").val();
    let selected_station_url = saved_stations[selected_station_index][0];
    update_station_name(selected_station_url, new_station_name).then(function(resp){
        refresh_stations();
        $("#station-name").html(new_station_name);
    });
});

$("#nav-status").click(function(){
    $("#status-page").show();
    $("#stations-page").hide();
    $("#alarm-time-page").hide();
    $("#nav-item-status").addClass("active");
    $("#nav-item-status").removeClass("active");
    $("#nav-item-alarm-time").removeClass("active");
});

$("#nav-stations").click(function(){
    $("#stations-page").show();
    $("#status-page").hide();
    $("#alarm-time-page").hide();
    $("#nav-item-stations").addClass("active");
    $("#nav-item-stations").removeClass("active");
    $("#nav-item-alarm-time").removeClass("active");
});
$("#nav-alarm-time").click(function(){
    $("#alarm-time-page").show();
    $("#status-page").hide();
    $("#stations-page").hide();
    $("#nav-item-alarm-time").addClass("active");
    $("#nav-item-stations").removeClass("active");
    $("#nav-item-status").removeClass("active");
});
