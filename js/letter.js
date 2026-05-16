String.prototype.pxWidth = function (font) {
	let canvas = String.prototype.pxWidth.canvas ||
		(String.prototype.pxWidth.canvas = document.createElement("canvas")),
		context = canvas.getContext("2d");
	font && (context.font = font);
	let metrics = context.measureText(this);
	return metrics.width;
}

function isNumber(str) {
	return !isNaN(parseInt(str));
}

function getPureStr(str) {
	let spices = str.split('^');
	let res = spices[0];
	for (let i = 1; i < spices.length; i++) {
		let tmp = spices[i];
		if (isNumber(tmp.charAt(0))) {
			let rm = parseInt(tmp).toString();
			tmp = tmp.substring(rm.length);
		}
		else {
			tmp = '^' + tmp;
		}
		res += tmp;
	}
	return res;
}

function scrollToBottom(smooth = true) {
	let dataContainer = document.getElementById('data');
	if (smooth) {
		dataContainer.scrollTo({
			top: dataContainer.scrollHeight,
			behavior: 'smooth'
		});
	} else {
		dataContainer.scrollTop = dataContainer.scrollHeight;
	}
}

let scrollInterval = null;

function startAutoScroll() {
	if (scrollInterval) return;
	scrollInterval = setInterval(function() {
		let dataContainer = document.getElementById('data');
		let currentScroll = dataContainer.scrollTop;
		let maxScroll = dataContainer.scrollHeight - dataContainer.clientHeight;
		let scrollDiff = maxScroll - currentScroll;
		if (scrollDiff > 5) {
			let scrollStep = Math.min(scrollDiff * 0.3, 30);
			dataContainer.scrollTop = currentScroll + scrollStep;
		}
	}, 30);
}

function stopAutoScroll() {
	if (scrollInterval) {
		clearInterval(scrollInterval);
		scrollInterval = null;
	}
}

$("#open").click(function () {
	if (!envelope_opened) {
		$('#wax-half').css('display', "block");
		new Typed('.letter', {
			strings: [
				"^1000",
				content.salutation + "<br><br>" +
				content.body + "<br><br><p style='float:right; display:block; width:" +
				content.sign + "px;'>^1000" + content.signature + "</p>"
			],
			typeSpeed: 30,
			backSpeed: 50,
			html: true,
			preStringTyped: function() {
				startAutoScroll();
			},
			onStringTyped: function() {
				scrollToBottom(true);
			},
			onComplete: function() {
				stopAutoScroll();
				scrollToBottom(true);
			}
		});
		$('#open').find("span").eq(0).css('background-position', "0 -150px");
		envelope_opened = true;
		let player = document.getElementById('music');
		if (player.paused) {
			player.play();
			$('#music_btn').css("display", "block");
		}
	}
});