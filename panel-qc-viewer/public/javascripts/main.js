const form = document.querySelector("form");
const log = document.querySelector("#log");
const single_channel_issues = ["missing_straws", "high_current_wires", "blocked_straws", "short_wires", "sparking_wires", "missing_anode", "missing_cathode" ] // the rest to be added
const doublet_channel_issues = ["missing_omega_pieces", "loose_omega_pieces"]

//
// All Panels Plot
//
const response = await fetch('allPanels');
const allPanelInfo = await response.json();
//console.log(allPanelInfo);
var single_channel_n_data = Array(single_channel_issues.length)
var panels = Array(allPanelInfo.length)
var hv_exists = Array(allPanelInfo.length).fill(0)
for (let i_panel = 0; i_panel < panels.length; i_panel++) {
    panels[i_panel] = allPanelInfo[i_panel]['id'];
    if (allPanelInfo[i_panel]['max_erf_fit'].length != 0) {
	hv_exists[i_panel] = 1;
    }
}
for (let i_issue = 0; i_issue < single_channel_issues.length; ++i_issue) {
    var n_issue = Array(allPanelInfo.length);
    var issue = single_channel_issues[i_issue];
//    console.log(issue)
    for (let i_panel = 0; i_panel < panels.length; i_panel++) {
	if (allPanelInfo[i_panel][issue] != null) {
	    n_issue[i_panel] = allPanelInfo[i_panel][issue].length;
	}
    }

    // Define Data
    single_channel_n_data[i_issue] = {name : issue,
					  x: panels,
					  y: n_issue,
					  mode:"markers",
					  type:"scatter"
					 }
}
var single_channel_issue_vs_panel_plot = document.getElementById('single_channel_issue_vs_panel_plot');
var xaxis = {title : {text : 'panel number'}, tickmode : "linear", tick0 : 0.0, dtick : 10.0, gridwidth : 2};
var yaxis = {title : {text : 'no. of channels with single-channel issues'}};
var layout = { title : {text: "All Single-Channel Issues vs Panel Number"},
	       xaxis : xaxis,
	       yaxis : yaxis,
	       scroolZoom : true };
Plotly.newPlot(single_channel_issue_vs_panel_plot, single_channel_n_data, layout);

var hv_data_vs_panel_plot = document.getElementById('hv_data_vs_panel_plot');
var hv_data_exists = {name : "hv_data_exists",
		      x: panels,
		      y: hv_exists,
		      mode:"markers",
		      type:"scatter"
		     }
var xaxis = {title : {text : 'panel number'}, tickmode : "linear", tick0 : 0.0, dtick : 10.0, gridwidth : 2};
var yaxis = {title : {text : ''}, 
	     tickmode: "array",
	     tickvals: [0, 1],
	     ticktext: ['no', 'yes']
	    };
var layout = { title : {text: "HV Data Exists?"},
	       xaxis : xaxis,
	       yaxis : yaxis,
	       scroolZoom : true };
Plotly.newPlot(hv_data_vs_panel_plot, [ hv_data_exists ], layout);

// var doublet_channel_n_data = Array(doublet_channel_issues.length)
// var panels = Array(allPanelInfo.length)
// for (let i_panel = 0; i_panel < panels.length; i_panel++) {
//     panels[i_panel] = allPanelInfo[i_panel]['id'];
// }
// for (let i_issue = 0; i_issue < doublet_channel_issues.length; ++i_issue) {
//     var n_issue = Array(allPanelInfo.length);
//     var issue = doublet_channel_issues[i_issue];
//     for (let i_panel = 0; i_panel < panels.length; i_panel++) {
// 	n_issue[i_panel] = allPanelInfo[i_panel][issue].length;
// //	n_issue[i_panel] = 1;
//     }

//     // Define Data
//     doublet_channel_n_data[i_issue] = {name : issue,
// 					  x: panels,
// 					  y: n_issue,
// 					  mode:"markers",
// 					  type:"scatter"
// 					 }
// }
// var doublet_channel_issue_vs_panel_plot = document.getElementById('doublet_channel_issue_vs_panel_plot');
// var xaxis = {title : {text : 'panel number'}, tickmode : "linear", tick0 : 0.0, dtick : 10.0, gridwidth : 2};
// var yaxis = {title : {text : 'no. of channels with doublet-channel issues'}};
// var layout = { title : {text: "All Doublet-Channel Issues vs Panel Number"},
// 	       xaxis : xaxis,
// 	       yaxis : yaxis,
// 	       scroolZoom : true };
// Plotly.newPlot(doublet_channel_issue_vs_panel_plot, doublet_channel_n_data, layout);
//
// Show issues with specific panel
//
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

	var this_title = "Panel "+panel_number;
	output = "Panel "+panel_number;
	if (panel_info.length>0) {
	    var this_panel_issues = panel_info[0]

	    var all_wires = Array(96).fill(0)
	    var wire_numbers = Array(96).fill(0)
	    for (let i = 0; i < all_wires.length; i++) {
		wire_numbers[i] = i;
	    }

	    var data = Array(single_channel_issues.length + doublet_channel_issues.length + 2) // +2 for max_erf_fit and rise_time
	    var total_issues = 0

	    for (let i = 0; i < doublet_channel_issues.length; i++) {
		var the_issue = doublet_channel_issues[i];
		var this_panel_doublets = Array(96).fill(0)
		var this_panel_issue = this_panel_issues[the_issue];
		for (let j = 0; j < this_panel_issue.length; j++) {
		    this_panel_doublets[this_panel_issue[j]] = 1;
		}
//		total_issues = total_issues + this_panel_issue.length
		var this_data = {
		    name : the_issue + " (DEMO)",
		    type : 'histogram',
		    histfunc : "sum",
		    x: wire_numbers,
		    y: this_panel_doublets,
		    xbins : { start : -0.5, end : 96.5, size : 1}
		};
		data[i] = this_data
	    }

	    for (let i = 0; i < single_channel_issues.length; i++) {
		var the_issue = single_channel_issues[i];
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
		    xbins : { start : 0, end : 96, size : 1}
		};
		data[doublet_channel_issues.length + i] = this_data
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

//	    var rise_times = this_panel_issues['rise_time'];
	    var rise_times = Array(48).fill(10);
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
	    
	    straw_status_plot = document.getElementById('straw_status_plot');
	    var xaxis = {title : {text : 'straw number'}, tickmode : "linear", tick0 : 0.0, dtick : 1.0, gridwidth : 2, range : [0, 96], domain : [0, 0.9]};
	    var yaxis = {title : {text : 'no. of issues'}};
	    var layout = { title : {text: this_title + " Straw/Wire Status"},
			   xaxis : xaxis,
			   yaxis : yaxis,
			   yaxis2: {
			       title: 'Max Erf Fit [nA]',
			       overlaying: 'y',
			       side: 'right',
			       titlefont: {color: 'red'},
			       tickfont: {color: 'red'}
			   },
			   yaxis3: {
			       title: 'Rise Time [min]',
			       overlaying: 'y',
			       side: 'right',
			       position : 0.95,
			       titlefont: {color: 'blue'},
			       tickfont: {color: 'blue'}
			   },
			   barmode : 'stack',
			   legend: {"orientation": "h"},
			   //		   margin: {t:0},
			   scroolZoom : true };
	    Plotly.newPlot(straw_status_plot, data, layout);	    
	    // total = missing_straws.length + high_current_wires.length + blocked_straws.length + sparking_wires.length;
	    output += " has "+total_issues+" bad channels: \n"
	    for (let i = 0; i < data.length-2; i++) {
		var the_issue = "";
		if (i < single_channel_issues.length) {
		    if (i == 0) {
			output += "\t single-channel issues: ";
		    }
		    the_issue = single_channel_issues[i];
		}
		else {
		    if (i == single_channel_issues.length) {
			output += "\n\t doublet-channel issues: ";
		    }
		    the_issue = doublet_channel_issues[i-single_channel_issues.length];
		}
		var this_panel_issue = this_panel_issues[the_issue];
		output += this_panel_issue.length + " " + the_issue;
		
		if (i != data.length-1) { output += ", "; }
	    }
	}
	else {
	    output += " not found!";
	}
    }
    else {
	output = "Input must be a number";
    }
	    
    document.getElementById("panel_info").innerHTML = output;
});

//
// Find panels
//
const findPanelsButton = document.getElementById('btnFindPanels');
findPanelsButton.addEventListener('click', async function () {

    let n_checks = 1;
    if (document.getElementById('uw_op_issue2_and').checked){// || document.getElementById('uw_op_issue2_or').checked) {
	n_checks = 2;
    }
    if (document.getElementById('uw_op_issue3_and').checked){// || document.getElementById('uw_op_issue3_or').checked) {
	n_checks = 3;
    }
    let uw_values = Array(n_checks)
    let uw_ops = Array(n_checks)
    let log_ops = Array(n_checks) // operator characters to write to the log
    let uw_issues = Array(n_checks)
    let uw_andors = Array(n_checks-1)
    let failed = false;
    for (let i_check = 1; i_check<=n_checks; ++i_check) {
	let uw_value = parseInt(document.getElementById('uw_value_issue'+i_check.toString()).value);
	if (!isNaN(uw_value)) {
	    let uw_op = '';
	    let log_op = '';
	    if (document.getElementById('uw_op_issue'+i_check.toString()+'_greater').checked) {
		uw_op = 'gt';
		log_op = '>';
	    }
	    else if (document.getElementById('uw_op_issue'+i_check.toString()+'_lesser').checked) {
		uw_op = 'lt';
		log_op = '<';
	    }
	    else if (document.getElementById('uw_op_issue'+i_check.toString()+'_equal').checked) {
		uw_op = 'eq';
		log_op = '=';
	    }
	    else if (document.getElementById('uw_op_issue'+i_check.toString()+'_greaterequal').checked) {
		uw_op = 'ge';
		log_op = '>=';
	    }
	    else if (document.getElementById('uw_op_issue'+i_check.toString()+'_lesserequal').checked) {
		uw_op = 'le';
		log_op = '<=';
	    }

	    let uw_issue = document.getElementById("issue"+i_check.toString()).value
	    uw_values[i_check-1] = uw_value;
	    uw_ops[i_check-1] = uw_op;
	    uw_issues[i_check-1] = uw_issue;
	    log_ops[i_check-1] = log_op;

	    var uw_andor = '';
	    if (i_check > 1) {
		if (document.getElementById('uw_op_issue'+i_check.toString()+'_and').checked) {
		    uw_andor = 'and';
		}
		else if (document.getElementById('uw_op_issue'+i_check.toString()+'_or').checked) {
		    uw_andor = 'or';
		}
		uw_andors[i_check-2] = uw_andor;
	    }
	}
	else {
	    failed = true;
	    break;
	}
    }
    var text = "";
    if (!failed) {
	var greater_info = await findPanels(uw_values, uw_ops, uw_issues, uw_andors);
	document.getElementById("log").innerHTML = JSON.stringify(
	    greater_info,
	    undefined,
	    2);

	var panels = Array(greater_info.length)
	for (let i = 0; i < greater_info.length; i++) {
	    panels[i] = greater_info[i]['id'];
	}
	text = panels.length + " panels with ";
	for (let i = 0; i < uw_values.length; ++i) {
	    if (i > 0) {
		text += " " + uw_andors[i-1] + " ";
	    }
	    text += log_ops[i]+uw_values[i]+" "+uw_issues[i];
	}
	text += ":\n "+panels;
    }
    else {
	text = "Problem with input";
    }
    document.getElementById("found_panel_info").innerHTML = text;
});

async function findPanels(uw_values, uw_ops, uw_issues, uw_andors) {
    var url = 'findPanels/';
    for (let i_issue = 0; i_issue < uw_values.length; ++i_issue) {
	if (i_issue > 0) {
	    url += "/" + uw_andors[i_issue-1] + "/";
	}
	url += uw_ops[i_issue] + "/" + uw_values[i_issue].toString() + "/" + uw_issues[i_issue];
    }
    console.log(url)
  const response = await fetch(url);
  const panelInfo = await response.json();
  return panelInfo;
}
