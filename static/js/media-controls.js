
//VOLUME BAR
//volume bar event
let volumeDrag = false;
let audio = {
    "muted": false
}
volume_change_cb = function(percentage){
    $('.volumeBar').css('width', percentage + '%');
}
$('.volume').on('mousedown', function (e) {
    volumeDrag = true;
    audio.muted = false;
    $('.sound').removeClass('muted');
    updateVolume(e.pageX);
});
$(document).on('mouseup', function (e) {
    if (volumeDrag) {
        volumeDrag = false;
        updateVolume(e.pageX);
    }
});
$(document).on('mousemove', function (e) {
    if (volumeDrag) {
        updateVolume(e.pageX);
    }
});

let updateVolume = function (x, vol) {
    let volume = $('.volume');
    let percentage;
    //if only volume have specificed
    //then direct update volume
    if (vol) {
        percentage = vol * 100;
    } else {
        let position = x - volume.offset().left;
        percentage = 100 * position / volume.width();
    }

    if (percentage > 100) {
        percentage = 100;
    }
    if (percentage < 0) {
        percentage = 0;
    }

    //update volume bar and video volume
    $('.volumeBar').css('width', percentage + '%');
    update_volume(percentage);
};