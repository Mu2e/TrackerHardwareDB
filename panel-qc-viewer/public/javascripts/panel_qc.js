
import { plot_panel_qc } from './panel_qc_plot.js'

const form = document.querySelector("form");
const log = document.querySelector("#log");

const showPanelButton = document.getElementById('btnShowPanel');
showPanelButton.addEventListener('click', async function () {
    var output = "";
    var panel_number = parseInt(document.getElementById('panel_number').value);    
    if (!isNaN(panel_number)) {
	const response = await fetch('getPanel/'+panel_number);
	const panel_info = await response.json();

	// Output the full return to the verbose output section
	document.getElementById("log").innerHTML = JSON.stringify(panel_info,
								  undefined,
								  2);

	output = "Panel "+panel_number;
	if (panel_info.length==0) {
	    output += " not found!";
	}
	else {
	    straw_status_plot = document.getElementById('straw_status_plot');
	    var returned_output = plot_panel_qc(panel_info, straw_status_plot);
	    output += returned_output;

	}
    }
    else {
	output = "Input must be a number";
    }
	    
    document.getElementById("panel_info").innerHTML = output;

    // Now do the table
    var cols = ["date_uploaded", "comment", "column_changed", "old_value", "new_value"];
    if (!isNaN(panel_number)) {
	const repairs_table_response = await fetch('getPanelRepairs/'+panel_number);
	const repairs_table = await repairs_table_response.json();

	var over_table = document.getElementById("panel_repairs_table");

	while (over_table.firstChild) {
	    over_table.removeChild(over_table.lastChild);
	}

	var table = document.createElement('TABLE');
	table.border = '1';

	var tableBody = document.createElement('TBODY');
	table.appendChild(tableBody);

	for (var i = 0; i < repairs_table.length+1; i++) {
	    var tr = document.createElement('TR');
	    tableBody.appendChild(tr);
	    tr.border = '1'

	    for (var j = 0; j < cols.length; j++) {
		var td = document.createElement('TD');
//		td.width = '75';
		td.style.border = "1px solid #000"
		if (i == 0) {
		    td.appendChild(document.createTextNode([cols[j]]));
		    td.style.textAlign = "center";
		    td.style.borderBottomWidth = "2px"
		}
		else {
		    td.appendChild(document.createTextNode(repairs_table[i-1][cols[j]]));
		}
		tr.appendChild(td);
	    }
	}
	over_table.appendChild(table);
    }
    else {
	output = "Input must be a number";
    }
});
