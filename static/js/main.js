let saved_stations = [];
let current_station = "";
let selected_station_index = -1;
function get_stations(){
    return new Promise(function(resolve, reject){
        $.ajax("/get_stations").done(function(resp){
            resolve(resp);
        }).fail(function (jqXHR, textStatus, errorThrown){
            reject(errorThrown);
        })
    })
}

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

function refresh_stations() {
    get_stations().then(function (resp) {
        get_current_station().then(function(resp2){
            update_current_station(resp2).then(function(){
                update_stations(resp).then(function () {
                    console.log("Success!");
                    render_stations();
                })
            })
        })
    })
}

$(document).ready(function(){
    refresh_stations();
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
    $("#nav-item-status").addClass("active");
    $("#nav-item-status").removeClass("active");
});

$("#nav-stations").click(function(){
    $("#stations-page").show();
    $("#status-page").hide();
    $("#nav-item-stations").addClass("active");
    $("#nav-item-stations").removeClass("active");
});
