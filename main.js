let envelope_opened = false;
let content = {
    salutation: "",
    signature: "",
    body: "",
    sign: 0
};

function playPause() {
    let player = document.getElementById('music');
    let play_btn = $('#music_btn');
    if (player.paused) {
        player.play();
        play_btn.attr('class', 'play');
    }
    else {
        player.pause();
        play_btn.attr('class', 'mute');
    }
}

let envelope_opened = false;
let content = {
    salutation: "",
    signature: "",
    body: "",
    sign: 0
};

function playPause() {
    let player = document.getElementById('music');
    let play_btn = $('#music_btn');
    if (player.paused) {
        player.play();
        play_btn.attr('class', 'play');
    }
    else {
        player.pause();
        play_btn.attr('class', 'mute');
    }
}

function scaleEnvelope() {
    let contact = $('#contact');
    let containerWidth = 600;
    let viewWidth = window.innerWidth;
    let scale = Math.min(1, (viewWidth * 0.92) / containerWidth);
    contact.css('transform', 'translateX(-50%) scale(' + scale + ')');

    let mtop;
    if (scale >= 1) {
        mtop = (window.innerHeight - 300) * 0.5;
    } else {
        mtop = Math.max(10, (window.innerHeight - 300 * scale) * 0.35);
    }
    contact.css('margin-top', mtop + 'px');
}

window.onload = function () {
    loadingPage();
    scaleEnvelope();
    $.ajaxSettings.async = true;
    $.getJSON("./font/content.json", function (result) {
        content.salutation = result.salutation;
        content.signature = result.signature;
        content.body = result.body;
        content.sign = getPureStr(content.signature).pxWidth('18px Satisfy, serif');
        document.title = result.title;
        $('#recipient').append(result.recipient);
        $('#flipback').text(result.sender);
        $('#music').attr('src', result.bgm);
        $('#envelope').fadeIn('slow');
        $('.heart').fadeOut('fast');
        let currentUrl = window.location.href;
        let firstIndex = currentUrl.indexOf("#");
        if (firstIndex <= 0) window.location.href = currentUrl + "#contact";
        scaleEnvelope();
    });
    $('body').css('opacity', '1');
    $('#jsi-cherry-container').css('z-index', '-99');
}

window.onresize = function () {
    let cherry_container = $('#jsi-cherry-container');
    let canvas = cherry_container.find('canvas').eq(0);
    canvas.height(cherry_container.height());
    canvas.width(cherry_container.width());
    loadingPage();
    scaleEnvelope();
}