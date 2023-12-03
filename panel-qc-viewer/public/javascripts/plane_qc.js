import { plot_panel_qc } from './panel_qc_plot.js'
import { draw_repairs_table } from './repairs_table.js'
import { get_panels_in_plane, get_panels_col_format } from './get_panels_in_plane.js'
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
	    var panels = get_panels_in_plane(plane_info[0]);
	    let six_col_format = get_panels_col_format(plane_info[0]);
	    if (panels.length == 0) {
		output += " no panels";
	    }

	    for (let i_panel = 0; i_panel < panels.length; ++i_panel) {
		var panel_number = panels[i_panel]
		
		const response = await fetch('getPanel/'+panel_number);
		const panel_info = await response.json();

		output += "Panel "+panel_number;
		if (panel_info.length==0) {
		    output += " not found!";
		}
		else {
		    let position="";
		    if (six_col_format) {
			position = "pos " + i_panel;
			if (i_panel % 2 == 0) {
			    position += " = top";
			}
			else {
			    position += " = bottom";
			}
			output += " (" + position + ")";
		    }
		    var plot_name = 'panel'+(i_panel+1).toString()+'_plot';
		    var straw_status_plot = document.getElementById(plot_name);
		    var returned_output = plot_panel_qc(panel_info, straw_status_plot, position);
		    output += returned_output + "\n\n";
		}
	    }
	}
	    
	document.getElementById("plane_info").innerHTML = output;

	// Now do the plane repairs table
	const repairs_table_response = await fetch('getPlaneRepairs/'+plane_number);
	const repairs_table_info = await repairs_table_response.json();
	var over_table = document.getElementById("plane_repairs_table");
	draw_repairs_table(repairs_table_info, over_table);



	// Now do the panel repairs table
//	var cols = ["panel_id", "date_uploaded", "comment", "column_changed", "old_value", "new_value"];

	var panels = get_panels_in_plane(plane_info[0]);
	let six_col_format = get_panels_col_format(plane_info[0]);

	for (let i_panel = 0; i_panel < panels.length; ++i_panel) {
	    var panel_number = panels[i_panel]
		
	    const repairs_panel_table_response = await fetch('getPanelRepairs/'+panel_number);
	    const repairs_panel_table_info = await repairs_panel_table_response.json();
	    var over_panel_table = document.getElementById("panel"+(i_panel+1).toString()+"_repairs_table");
	    while (over_panel_table.firstChild) {
		over_panel_table.removeChild(over_panel_table.lastChild);
	    }
	    draw_repairs_table(repairs_panel_table_info, over_panel_table, 'panel_id');
	}
    }
    else {
	output = "Input must be a number";
    }
});
