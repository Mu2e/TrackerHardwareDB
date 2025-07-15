import { single_channel_issues } from './single_channel_issues.js'
import { single_panel_issues, single_panel_issue_names } from './single_panel_issues.js'

export function plot_panel_qc(panel_info, straw_status_plot, summary_table, position="") {

    const single_ch_issues = single_channel_issues(); // the rest to be added

    var this_panel_issues = panel_info[0]
    var this_title = "Panel "+this_panel_issues["panel_id"];
    if (position != "") {
	this_title += " (" + position + ")";
    }

    var all_wires = Array(96).fill(0)
    var wire_numbers = Array(96).fill(0)
    for (let i = 0; i < all_wires.length; i++) {
	wire_numbers[i] = i;
    }

    var data = Array(single_ch_issues.length +2) // +2 for max_erf_fit and rise_time
    var total_issues = 0

    for (let i = 0; i < single_ch_issues.length; i++) {
	var the_issue = single_ch_issues[i];
	var this_panel_straws = Array(96).fill(0)
	var this_panel_issue = this_panel_issues[the_issue];
	for (let j = 0; j < this_panel_issue.length; j++) {
	    this_panel_straws[this_panel_issue[j]] = 1;
	}
	total_issues = total_issues + this_panel_issue.length
	var this_data = {
	    name : the_issue,
	    type : 'histogram',
	    histfunc : "sum",
	    x: wire_numbers,
	    y: this_panel_straws,
	    xbins : { start : -0.5, end : 96.5, size : 1}
	};
	data[i] = this_data
    }

    var max_erf_fits = this_panel_issues['max_erf_fit'];
    var doublet_numbers = Array(48).fill(0)
    for (let i = 0; i < doublet_numbers.length; i++) {
	doublet_numbers[i] = (2*i+0.5);
    }
    var max_erf_fit_data = {
	name : 'max_erf_fit',
	type : 'scatter',
	x: doublet_numbers,
	y: max_erf_fits,
	yaxis : 'y2',
	mode : 'lines+markers',
	marker : { color : 'red' },
	line : { color : 'red' }
    };	    
    data[data.length-2] = max_erf_fit_data;

    var rise_times = this_panel_issues['rise_time'];
    var rise_time_data = {
	name : 'rise_time',
	type : 'scatter',
	x: doublet_numbers,
	y: rise_times,
	yaxis : 'y3',
	mode : 'lines+markers',
	marker : { color : 'blue' },
	line : { color : 'blue' }
    };	    
    data[data.length-1] = rise_time_data;
    

    var xaxis = {title : {text : 'straw number'}, tickmode : "linear", tick0 : 0.0, dtick : 1.0, gridwidth : 2, range : [-0.5, 96.5], domain : [0, 0.9]};
    var yaxis = {title : {text : 'no. of issues'}};
    var layout = { title : {text: this_title + " Straw/Wire Status"},
		   xaxis : xaxis,
		   yaxis : yaxis,
		   yaxis2: {
		       title: 'Max Erf Fit [nA]',
		       overlaying: 'y',
		       side: 'right',
		       titlefont: {color: 'red'},
		       tickfont: {color: 'red'},
		       zerolinecolor : 'red',
		       showgrid : false,
		       range : [-0.2, 1.2]
		   },
		   yaxis3: {
		       title: 'Rise Time [min]',
		       overlaying: 'y',
		       side: 'right',
		       position : 0.95,
		       titlefont: {color: 'blue'},
		       tickfont: {color: 'blue'},
		       showgrid : false,
		       zerolinecolor : 'blue',
		       range : [0, 60]
		   },
		   barmode : 'stack',
		   legend: {"orientation": "h"},
		   //		   margin: {t:0},
		   scroolZoom : true };
    Plotly.newPlot(straw_status_plot, data, layout);	    

    // total = missing_straws.length + high_current_wires.length + blocked_straws.length + sparking_wires.length;
    var output = " has "+total_issues+" issues: \n"
    var first = true;
    for (let i = 0; i < data.length-2; i++) {
	var the_issue = "";
	if (i < single_ch_issues.length) {
	    the_issue = single_ch_issues[i];
	}
	var this_panel_issue = this_panel_issues[the_issue];
	if (this_panel_issue.length > 0) {
	    if (first == true) {
	    	output += "\t ";
		first = false;
	    }
	    else {
		output += ", ";
	    }
	    output += this_panel_issue.length + " " + the_issue + " (";
	    for (let i_channel = 0; i_channel < this_panel_issue.length; ++i_channel) {
		output += "#" + this_panel_issue[i_channel];
		if (i_channel < this_panel_issue.length-1) {
		    output += ",";
		}
	    }
	    output += ")";
	}
//	if (i != data.length-1) { output += ", "; }
    }

    const single_pan_issues = single_panel_issues();
    const single_pan_issue_names = single_panel_issue_names();

    let emojii_yes = 9989;
    let emojii_no = 10060;
    let emojii_unknown = 10068;

    // clear previous table
    while (summary_table.firstChild) {
	summary_table.removeChild(summary_table.lastChild);
    }

    var table = document.createElement('TABLE');
    table.border = '1';
    var tableBody = document.createElement('TBODY');
    table.appendChild(tableBody);

    var tr1 = document.createElement('TR');
    tableBody.appendChild(tr1);
    tr1.border = '1'
    var tr2 = document.createElement('TR');
    tableBody.appendChild(tr2);
    tr2.border = '1'

    // two rows: row 1 = issue name, row 2= results
    // columns are the individual issues
    for (let i_issue = 0; i_issue < single_pan_issues.length; ++i_issue) {
	var issue = single_pan_issues[i_issue];
	var issue_name = single_pan_issue_names[i_issue];
	var emojii_result = emojii_unknown;
	if (this_panel_issues[issue] != null) {
	    if (issue != 'max_erf_fit') {
	//	output += this_panel_issues[issue]; // don't need to write this now
		if (this_panel_issues[issue] == true) { emojii_result = emojii_yes; }
		else if (this_panel_issues[issue] == false) { emojii_result = emojii_no; }
	    }
	    else {
		output += "\n\t Fe55 data files: "; // stll want to write out Fe55 data file names
		var maxerf_risetime_filenames = this_panel_issues["maxerf_risetime_filenames"];
		if (maxerf_risetime_filenames.length == 0) {
		    output += "none";
		    emojii_result = emojii_no;
		}
		else {
		    emojii_result = emojii_yes;
		    for (let i_filename = 0; i_filename < maxerf_risetime_filenames.length; ++i_filename) {
			output += maxerf_risetime_filenames[i_filename];
			if (i_filename < maxerf_risetime_filenames.length-1) {
			    output += ", ";
			}
		    }
		}
	    }
	}
	else {
	    if (issue == 'hv_test_done') { // for hv_test_done, if we have information about sparking wires etc. then we can assume the test was done even if its unknown
		if (this_panel_issues['high_current_wires'].length != 0 ||
		    this_panel_issues['sparking_wires'].length != 0 ||
		    this_panel_issues['short_wires'].length != 0) {
		    
//		    output += "yes";
		    emojii_result = emojii_yes;
		}
	    }
	    else {
		emojii_result = emojii_unknown;
	    }
	}

	var td1 = document.createElement('TD');
	td1.style.border = "1px solid #000"
	td1.appendChild(document.createTextNode(issue_name));
	td1.style.textAlign = "center";
	td1.style.borderBottomWidth = "1px"
	tr1.appendChild(td1)

	var td2 = document.createElement('TD');
	td2.style.border = "1px solid #000"
	td2.appendChild(document.createTextNode(String.fromCodePoint(emojii_result)));
	td2.style.textAlign = "center";
	td2.style.borderBottomWidth = "1px"
	tr2.appendChild(td2)
    }
    summary_table.append(table);

    // Output the DRAC ID
    output += "\n\t DRAC ID = " + this_panel_issues['drac_id'];
    output += "\n\t Survey Hole Issues? (hv, mid, cal) = " + this_panel_issues['survey_hole_problem_hv'] + ", " + this_panel_issues['survey_hole_problem_mid'] + ", " + this_panel_issues['survey_hole_problem_cal'];

    return output;
}
