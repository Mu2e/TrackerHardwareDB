const showEarBoardButton = document.getElementById('btnShowEarBoard');
showEarBoardButton.addEventListener('click', async function () {
    var output = "";
    var panel_number = parseInt(document.getElementById('panel_number').value);

    if (!isNaN(panel_number)) {
	var this_title = "Panel "+panel_number;
	console.log(this_title);

	var img_earboard = document.getElementById('img_earboard');
	img_earboard.src =  "images/earboard/plot_" + panel_number.toString().padStart(3,'0') + ".pdf";

	const response = await fetch('getEarBoard/'+panel_number);
	const panel_info = await response.json();

	document.getElementById("earboard_result").innerHTML = "pass/fail";
	//img_earboard.onerror = smooth_data;
	//img_earboard.onload = function() { document.getElementById("smooth_filename").innerHTML = img_earboard.src; }
	//smooth_data();
	
    }
    else {
	output = "Input must be a number";
    }
	    
//    document.getElementById("panel_info").innerHTML = output;
});
