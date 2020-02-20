let saved_stations = [];

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
            saved_stations = JSON.parse(resp_json);
            resolve();
        } catch (e) {
            reject(e);
        }
    })
}

$(document).ready(function(){
    get_stations().then(function(resp){
        update_stations(resp).then(function(){
            console.log("Success!");
        })
    })
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
                saved_stations.push(new_station_url);
            });
        }
    }
    
    console.log("Station URL: " + verified_url);
})