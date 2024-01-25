import { plot_panel_qc } from './panel_qc_plot.js'
import { draw_repairs_table } from './repairs_table.js'
import { get_panels_in_plane, get_panels_col_format } from './get_panels_in_plane.js'
import { stdDev } from "./stats.js"

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
	output = "Plane "+plane_number;
	if (plane_info.length==0) {
	    output += " not found!";
	}
	else {
	    output += " (constructed: " + plane_info[0]['construction_start_date'] + " - " + plane_info[0]['construction_end_date'] + ")\n";
	    output += "\n"

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

	// Now make the measurement plots
	let measurement_output = "Plane Measurements\n";
	measurement_output += "==================\n"

	const height_response = await fetch('getMeasurements/plane/heights/'+plane_number);
	const height_measurements = await height_response.json();
	if (height_measurements.length != 0) {
	    measurement_output += "\nHeight Measurements: see plot\n";
//	    console.log(height_measurements);
	    //	console.log(stdDev(heights));
	    let heights = Array();
	    let first_date = height_measurements[0]['date_taken']
	    for (let i_height_measurement = 0; i_height_measurement < height_measurements.length; ++i_height_measurement) {
		if (height_measurements[i_height_measurement]['date_taken'] != first_date) {
		    break;
		}
		heights.push(height_measurements[i_height_measurement]['height_inches']);
	    }
	    var height_measurements_data = {name : "Plane " + plane_number + " Height Measurements",
					    x: heights,
					    //					    y: vals,
					    type:"histogram",
					    xbins : { start : -0.02, end : 0.02, size : 0.001}
					   }
	    
	    var height_measurement_plot = document.getElementById("height_measurement_plot");
	    var xaxis = {title : {text : 'planarity [inches]'}, tickmode : "linear", tick0 : -0.02, dtick : 0.001, gridwidth : 2};
	    //	var yaxis = {title : {text : 'no. of channels with issues'}};
	    var layout = { title : {text: "Most Recent Height Measurements (from " + first_date + ")"},
			   xaxis : xaxis,
			   //		       yaxis : yaxis,
		       scroolZoom : true,
			   //		       showlegend : true,
			   //		       barmode : 'stack',
//		       shapes: [ {type: 'line', x0: 0, y0: 30.0, x1: planes.length, y1: 30.0, line:{ color: 'rgb(0, 0, 0)', width: 4, dash:'dot'} } ]
			   annotations : [{ xref : 'paper', yref : 'paper', x : 0.5, y : 1, showarrow : false,
					    text : 'Std Dev = ' + stdDev(heights).toFixed(4) + ' inches', 
					    font : { size : 16 } 
					  }]
			 };
	    Plotly.newPlot(height_measurement_plot, [height_measurements_data], layout);
	}
	else {
	    measurement_output += "\nHeight Measurements: none found\n";
	}

	const pin_response = await fetch('getMeasurements/plane/pins/'+plane_number);
	const pin_measurements = await pin_response.json();
	if (pin_measurements.length != 0) {
	    let first_date = pin_measurements[0]['date_taken']

	    let nominal_pin = 0.187;
	    measurement_output += "\nPin-to-Pin Measurements (from " + first_date + ", nominal = " + nominal_pin + "\"):\n";
	    let total_nominal_diff = 0;
	    let total_pins = 0;
	    for (let i_pin_measurement = 0; i_pin_measurement < pin_measurements.length; ++i_pin_measurement) {
		if (pin_measurements[i_pin_measurement]['date_taken'] != first_date) {
		    break;
		}
		let pin_inches = pin_measurements[i_pin_measurement]["pin_inches"];
		let nominal_diff = pin_inches - nominal_pin;
		total_nominal_diff  += nominal_diff;
		total_pins++;
		measurement_output += pin_measurements[i_pin_measurement]['top_panel_id'] + " - " + pin_measurements[i_pin_measurement]['bottom_panel_id'] + " (pos. " + pin_measurements[i_pin_measurement]['pin_position'] + ") = " +  pin_inches + "\" (" +  nominal_diff.toFixed(3) + "\" from nominal)\n";
	    }
	    let mean_nominal_diff = total_nominal_diff / total_pins;
	    measurement_output += "Mean diff. from nominal = " + mean_nominal_diff.toFixed(3) + "\"\n"
	}
	else {
	    measurement_output += "\nPin-to-Pin Measurements: none found\n";
	}

	const gap_response = await fetch('getMeasurements/plane/gaps/'+plane_number);
	const gap_measurements = await gap_response.json();
	if (gap_measurements.length != 0) {
	    let first_date = gap_measurements[0]['date_taken']

	    measurement_output += "\nGap Measurements (from " + first_date + "):\n";
	    for (let i_gap_measurement = 0; i_gap_measurement < gap_measurements.length; ++i_gap_measurement) {
		if (gap_measurements[i_gap_measurement]['date_taken'] != first_date) {
		    break;
		}
		let gap_ccw_mm = gap_measurements[i_gap_measurement]["gap_ccw_mm"];
		measurement_output += gap_measurements[i_gap_measurement]['first_panel_id'] + ", " + gap_measurements[i_gap_measurement]['second_panel_id'] + " (ccw): " +  gap_ccw_mm.toFixed(3) + " mm\n";
	    }
	}
	else {
	    measurement_output += "\nGap Measurements: none found\n";
	}

	measurement_output += "\nLeak Measurements:\n";
	let panel_leak_budget = 0.014;
	let plane_leak_budget = panel_leak_budget*6;
	measurement_output += "(panel leak budget: " + panel_leak_budget + " sccm, plane leak budget: " + plane_leak_budget + " sccm)\n";
	var panels = get_panels_in_plane(plane_info[0]);
	let plane_leak_sccm = 0;
	for (let i_panel = 0; i_panel < panels.length; ++i_panel) {
	    let panel_number = panels[i_panel];
	    const leak_response = await fetch('getMeasurements/panel/leaks/'+panel_number);
	    const leak_measurements = await leak_response.json();
	    if (leak_measurements.length != 0) {
		// Only take most recent leak measurement
		let leak_sccm = leak_measurements[0]["leak_sccm"];
		plane_leak_sccm += leak_sccm;
//		let frac_of_budget = (leak_sccm / panel_leak_budget)*100;
		measurement_output += panel_number + ": " + leak_measurements[0]['date_taken'] + " (" + leak_measurements[0]['comment'] + ") = " +  leak_sccm.toFixed(4) + " sccm\n";// (" + frac_of_budget.toFixed(1) + "% of panel leak budget)\n";
	    }
	    else {
		measurement_output += panel_number + ": none found\n";
	    }
	}
	let frac_of_plane_budget = (plane_leak_sccm / plane_leak_budget)*100;
	measurement_output += "Plane Leak Rate = " + plane_leak_sccm.toFixed(4) + " sccm (" + frac_of_plane_budget.toFixed(1) + "% of plane leak budget)\n";


	document.getElementById("measurement_info").innerHTML = measurement_output;

    }
    else {
	output = "Input must be a number";
    }
});
