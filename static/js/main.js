let saved_stations = [];
let current_station = "";
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
    let stationsHTML = "<ul class='list-group'>";
    for(let i = 0; i < saved_stations.length; i++){
        stationsHTML += "<li id=\"saved-station-" + i + "\" class='list-group-item'>" + saved_stations[i][1] + "\t:\t" + saved_stations[i][0] + "</li>";
    }
    stationsHTML += "</ul>";
    $("#saved-stations").html(stationsHTML);
    for(let i = 0; i < saved_stations.length; i++){
        $("#saved-station-" + i).click(function(){
            set_current_station(saved_stations[i][0]).then(function(){
                for(let j = 0; j < saved_stations.length; j++){
                    if(j == i){
                        $("#saved-station-" + i).addClass("active");
                    } else {
                        $("#saved-station-" + j).removeClass("active");
                    }
                }

            })
        })
    }
}

function refresh_stations() {
    get_stations().then(function (resp) {
        update_stations(resp).then(function () {
            console.log("Success!");
            render_stations();
        })
    })
}

$(document).ready(function(){
    refresh_stations();
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
})