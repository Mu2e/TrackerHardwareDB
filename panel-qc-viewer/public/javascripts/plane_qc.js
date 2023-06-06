import { plot_panel_qc } from './panel_qc_plot.js'
const form = document.querySelector("form");
const log = document.querySelector("#log");

const showPlaneButton = document.getElementById('btnShowPlane');
showPlaneButton.addEventListener('click', async function () {
    var output = "";
    var plane_number = parseInt(document.getElementById('plane_number').value);
    if (!isNaN(plane_number)) {
	const response = await fetch('getPlane/'+plane_number);
	const plane_info = await response.json();

	// // Output the full return to the verbose output section
	// document.getElementById("log").innerHTML = JSON.stringify(plane_info,
	// 							  undefined,
	// 							  2);

	// Fill with DUMMY data for the time being
	output = "Plane "+plane_number+":\n";
	if (plane_info.length==0) {
	    output += " not found!";
	}
	else {
	    var panels = Array(6).fill(0);
	    for (let i_panel = 0; i_panel < 6; ++i_panel) {
		panels[i_panel] = plane_info[0]['panel_ids'][i_panel];
	    }

	    for (let i_panel = 0; i_panel < 6; ++i_panel) {
		var panel_number = panels[i_panel]
		var this_title = "Panel "+panel_number.toString();
		
		const response = await fetch('getPanel/'+panel_number);
		const panel_info = await response.json();

		output += "Panel "+panel_number;
		if (panel_info.length==0) {
		    output += " not found!";
		}
		else {
		    var plot_name = 'panel'+(i_panel+1).toString()+'_plot';
		    var straw_status_plot = document.getElementById(plot_name);
		    var returned_output = plot_panel_qc(panel_info, straw_status_plot);
		    output += returned_output + "\n\n";
		}
	    }
	}
    }
    else {
	output = "Input must be a number";
    }
	    
    document.getElementById("plane_info").innerHTML = output;
});
