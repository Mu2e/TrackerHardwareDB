import { single_channel_issues } from './single_channel_issues.js'
import { single_panel_issues, single_panel_issue_names } from './single_panel_issues.js'
import { get_panels_in_plane } from './get_panels_in_plane.js'
const single_ch_issues = single_channel_issues();
const single_pan_issues = single_panel_issues();
const single_pan_issue_names = single_panel_issue_names();

var yes = 1.0;
var no = 0.5;
var unknown = 0;


//
// All Panels Plot
//
const response = await fetch('allPanels');
const allPanelInfo = await response.json();
//console.log(allPanelInfo);
var single_channel_n_data = Array(single_ch_issues.length)
var single_panel_data = Array(single_pan_issues.length)

var panels = Array(allPanelInfo.length)
var panel_num_map = new Map();
var highest_panel_id = 0;

for (let i_panel = 0; i_panel < panels.length; i_panel++) {
    panels[i_panel] = allPanelInfo[i_panel]['panel_id'];
    panel_num_map.set(allPanelInfo[i_panel]['panel_id'], i_panel);
    if (allPanelInfo[i_panel]['panel_id'] > highest_panel_id) {
	highest_panel_id = allPanelInfo[i_panel]['panel_id'];
    }
}

for (let i_issue = 0; i_issue < single_ch_issues.length; ++i_issue) {
    var n_issue = Array(allPanelInfo.length);
    var issue = single_ch_issues[i_issue];
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
					  type:"bar"
					 }
}
var single_channel_issue_vs_panel_plot = document.getElementById('single_channel_issue_vs_panel_plot');
var xaxis = {title : {text : 'panel number'}, tickmode : "linear", tick0 : 0.0, dtick : 10.0, gridwidth : 2};
var yaxis = {title : {text : 'no. of channels with issues'}};
var layout = { title : {text: "All Issues vs Panel Number"},
	       xaxis : xaxis,
	       yaxis : yaxis,
	       scroolZoom : true,
	       barmode : "stack",
	       shapes: [ {type: 'line', x0: 0, y0: 5.0, x1: highest_panel_id, y1: 5.0, line:{ color: 'rgb(0, 0, 0)', width: 4, dash:'dot'} } ]
	     };
Plotly.newPlot(single_channel_issue_vs_panel_plot, single_channel_n_data, layout);

for (let i_issue = 0; i_issue < single_pan_issues.length; ++i_issue) {
    var vals = Array(allPanelInfo.length);
    var issue = single_pan_issues[i_issue];
//    console.log(issue)
    for (let i_panel = 0; i_panel < panels.length; i_panel++) {
	if (allPanelInfo[i_panel][issue] != null) {
	    if (issue == 'max_erf_fit') {
		if (allPanelInfo[i_panel][issue].length != 0) {
		    vals[i_panel] = yes;
		}
		else {
		    vals[i_panel] = no;
		}
	    }
	    else {
		if (allPanelInfo[i_panel][issue] == true) {
		    vals[i_panel] = yes;
		}
		else if (allPanelInfo[i_panel][issue] == false) {
		    vals[i_panel] = no;
		}
	    }
	}
	else {
	    vals[i_panel] = unknown;
	}
    }

    // Define Data
    single_panel_data[i_issue] = {name : single_pan_issue_names[i_issue],
    				  x: panels,
    				  y: vals,
    				  mode:"markers",
    				  type:"scatter"
    				 }
}
var has_data_vs_panel_plot = document.getElementById('has_data_vs_panel_plot');
var xaxis = {title : {text : 'panel number'}, tickmode : "linear", tick0 : 0.0, dtick : 10.0, gridwidth : 2};
var yaxis = {title : {text : ''}, 
 	     tickmode: "array",
 	     tickvals: [no, yes, unknown],
 	     ticktext: ['no', 'yes', 'unknown']
 	    };
var layout = { title : {text: "Yes / No / Unknown Questions"},
 	       xaxis : xaxis,
 	       yaxis : yaxis,
 	       scroolZoom : true };

Plotly.newPlot(has_data_vs_panel_plot, single_panel_data, layout);

////
// Plane QC Summary
//

const plane_response = await fetch('allPlanes');
const allPlaneInfo = await plane_response.json();
//console.log(allPlaneInfo)
var planes = Array(allPlaneInfo.length)
var single_channel_n_data_plane = Array(single_ch_issues.length)
var single_panel_data_plane = Array(single_pan_issues.length)

for (let i_issue = 0; i_issue < single_ch_issues.length; ++i_issue) {
    var n_issue = Array(allPlaneInfo.length);
    var issue = single_ch_issues[i_issue];
//    console.log(issue)
    for (let i_plane = 0; i_plane < planes.length; i_plane++) {
	n_issue[i_plane] = 0;
	planes[i_plane] = allPlaneInfo[i_plane]['plane_id'];
	let panels = get_panels_in_plane(allPlaneInfo[i_plane])
	for (let i_panel = 0; i_panel < panels.length; ++i_panel){
	    let panel_number = panels[i_panel];
	    const panel_info = allPanelInfo[panel_num_map.get(panel_number)];
	    if (panel_info[issue] != null) {
		n_issue[i_plane] += panel_info[issue].length;
	    }
	}
    }

    // Define Data
    single_channel_n_data_plane[i_issue] = {name : issue,
					  x: planes,
					  y: n_issue,
					  mode:"markers",
					  type:"bar"
					 }
}

for (let i_issue = 0; i_issue < single_pan_issues.length; ++i_issue) {
    var vals = Array(allPanelInfo.length);
    var issue = single_pan_issues[i_issue];

    for (let i_plane = 0; i_plane < planes.length; i_plane++) {
	vals[i_plane] = 0;
	planes[i_plane] = allPlaneInfo[i_plane]['plane_id'];
	let panels = get_panels_in_plane(allPlaneInfo[i_plane])

	for (let i_panel = 0; i_panel < panels.length; ++i_panel){
	    let panel_number = panels[i_panel];
	    const panel_info = allPanelInfo[panel_num_map.get(panel_number)];
	    if (panel_info[issue] != null) {
		if (issue == 'max_erf_fit') {
		    if (panel_info[issue].length != 0) {
			vals[i_plane] += 1;
		    }
		}
		else {
		    if (panel_info[issue] == true) {
			vals[i_plane] += 1;
		    }
		}
	    }
	}
    }

    // Define Data
    single_panel_data_plane[i_issue] = {name : single_pan_issue_names[i_issue],
					x: planes,
					y: vals,
					mode:"markers",
					type:"bar"
				       }
}


var single_channel_issue_vs_plane_plot = document.getElementById('single_channel_issue_vs_plane_plot');
var xaxis = {title : {text : 'plane number'}, tickmode : "linear", tick0 : 0.0, dtick : 1.0, gridwidth : 2};
var yaxis = {title : {text : 'no. of channels with issues'}};
var layout = { title : {text: "All Issues vs Plane Number"},
	       xaxis : xaxis,
	       yaxis : yaxis,
	       scroolZoom : true,
	       barmode : 'stack',
	       shapes: [ {type: 'line', x0: 0, y0: 30.0, x1: planes.length, y1: 30.0, line:{ color: 'rgb(0, 0, 0)', width: 4, dash:'dot'} } ]
	     };
Plotly.newPlot(single_channel_issue_vs_plane_plot, single_channel_n_data_plane, layout);

var has_data_vs_plane_plot = document.getElementById('has_data_vs_plane_plot');
var xaxis = {title : {text : 'plane number'}, tickmode : "linear", tick0 : 0.0, dtick : 1.0, gridwidth : 2};
var yaxis = {title : {text : 'Number of panels in plane'}, tick0 : 0.0, dtick : 1, range : [0, 7] };
var layout = { title : {text: "Number of panels in plane that..."},
	       xaxis : xaxis,
	       yaxis : yaxis,
	       scroolZoom : true};
Plotly.newPlot(has_data_vs_plane_plot, single_panel_data_plane, layout);
