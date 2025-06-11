import { single_channel_issues, dead_channel_issues } from './single_channel_issues.js'
import { single_panel_issues, single_panel_issue_names } from './single_panel_issues.js'
import { get_panels_in_plane } from './get_panels_in_plane.js'
const single_ch_issues = single_channel_issues();
const dead_ch_issues = dead_channel_issues();
const single_pan_issues = single_panel_issues();
const single_pan_issue_names = single_panel_issue_names();

var yes = 1.0;
var no = 0.5;
var unknown = 0;

let colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', 'black', 'navy', 'olive', 'powderblue', 'darksalmon', 'aquamarine', 'salmon', 'mediumvioletred' ];

let yes_no_colors = ['blue', 'red', 'lightblue', 'pink', 'darkblue', 'darkred', 'aquamarine', 'crimson', 'midnightblue', 'darksalmon', 'powderblue', 'mediumvioletred']//#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', 'black', 'navy', 'olive' ];;//['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', 'green', 'red', 'lightgreen', 'lightred', 'darkgreen', 'darkred', 'white', 'black'];


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

var n_dead_channels = Array(allPanelInfo.length); // keep track of total number of issues without double-counting
for (let i_issue = 0; i_issue < single_ch_issues.length; ++i_issue) {
    var n_issue = Array(allPanelInfo.length);
    var issue = single_ch_issues[i_issue];
    //    console.log(issue)
    for (let i_panel = 0; i_panel < panels.length; i_panel++) {
	if (i_issue == 0) {
	    n_dead_channels[i_panel] = Array();
	}
	if (allPanelInfo[i_panel][issue] != null) {
	    n_issue[i_panel] = allPanelInfo[i_panel][issue].length;
	    if (dead_ch_issues.includes(issue)) {
		n_dead_channels[i_panel] = n_dead_channels[i_panel].concat(allPanelInfo[i_panel][issue]); // this will contain all the channnel numbers (inc. duplicates)
	    }
	}
    }

    // Define Data
    var default_visible = '';
    single_channel_n_data[i_issue] = {name : issue,
					  x: panels,
					  y: n_issue,
					  mode:"markers",
				      type:"bar",
				      visible:default_visible
					 }
}
for (let i_panel = 0; i_panel < panels.length; i_panel++) {
    n_dead_channels[i_panel] = [...new Set(n_dead_channels[i_panel])].length; // remove duplicate channel numbers
}
var dead_channels_data = {name : 'total',
			  x: panels,
			  y: n_dead_channels,
			  mode:"markers",
			  type:"bar",
			 }

var xaxis = {title : {text : 'panel number'}, tickmode : "linear", tick0 : 0.0, dtick : 10.0, gridwidth : 2};
var yaxis = {title : {text : 'no. of dead channels'}};
var layout = { title : {text: "N Dead Channels vs Panel Number"},
	       xaxis : xaxis,
	       yaxis : yaxis,
	       scroolZoom : true,
	       barmode : "stack",
	       shapes: [ {type: 'line', x0: 0, y0: 5.0, x1: highest_panel_id, y1: 5.0, line:{ color: 'rgb(0, 0, 0)', width: 4, dash:'dot'} } ],
	       colorway : colors
	     };

var dead_channels_vs_panel_plot = document.getElementById('dead_channels_vs_panel_plot');
Plotly.newPlot(dead_channels_vs_panel_plot, [dead_channels_data], layout);

var dead_channel_definition = document.getElementById('dead_channel_definition');
dead_channel_definition.innerHTML = "Dead channel definition: "+dead_ch_issues.slice(0,7).join(", ") + "\n" + dead_ch_issues.slice(8).join(", ");

var single_channel_issue_vs_panel_plot = document.getElementById('single_channel_issue_vs_panel_plot');
layout.title.text = "Channel-level QC vs Panel Number";
yaxis.title.text = 'no. of channels with issues';
layout.shapes = Array();
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
	    if (issue == 'hv_test_done') { // for hv_test_done, if we have information about sparking wires etc. then we can assume the test was done even if its unknown
		if (allPanelInfo[i_panel]['high_current_wires'].length != 0 ||
		    allPanelInfo[i_panel]['sparking_wires'].length != 0 ||
		    allPanelInfo[i_panel]['short_wires'].length != 0) {

		    vals[i_panel] = yes;
		}
	    }
	    vals[i_panel] = unknown;
	}
    }

    // Define Data
    single_panel_data[i_issue] = {name : single_pan_issue_names[i_issue] + " (Y = " + vals.filter(x => x===yes).length + ", N = " + vals.filter(x => x===no).length + ", ? = " + vals.filter(x => x === unknown).length + ")",
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
 	       scroolZoom : true,
	       colorway : colors
	     };
Plotly.newPlot(has_data_vs_panel_plot, single_panel_data, layout);

////
// Plane QC Summary
//

const plane_response = await fetch('allPlanes');
const allPlaneInfo = await plane_response.json();
//console.log(allPlaneInfo)
var planes = Array(allPlaneInfo.length)
var single_channel_n_data_plane = Array(single_ch_issues.length)
var single_panel_data_plane = Array(2*single_pan_issues.length) // 2* because pass and fail

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
    var default_visible = '';
    single_channel_n_data_plane[i_issue] = {name : issue,
					    x: planes,
					    y: n_issue,
					    mode:"markers",
					    type:"bar",
					    visible:default_visible
					   }
}

// Count total dead channels
var n_dead_channels_plane = Array(allPlaneInfo.length).fill(0);
for (let i_plane = 0; i_plane < planes.length; i_plane++) {
    planes[i_plane] = allPlaneInfo[i_plane]['plane_id'];
    let panels = get_panels_in_plane(allPlaneInfo[i_plane])
    for (let i_panel = 0; i_panel < panels.length; ++i_panel){
	let panel_number = panels[i_panel];
	n_dead_channels_plane[i_plane] += n_dead_channels[panel_num_map.get(panel_number)];
    }
}


for (let i_issue = 0; i_issue < single_pan_issues.length; ++i_issue) {
    var passes = Array(allPanelInfo.length);
    var fails = Array(allPanelInfo.length);
    var issue = single_pan_issues[i_issue];

    for (let i_plane = 0; i_plane < planes.length; i_plane++) {
	passes[i_plane] = 0;
	fails[i_plane] = 0;
	planes[i_plane] = allPlaneInfo[i_plane]['plane_id'];
	let panels = get_panels_in_plane(allPlaneInfo[i_plane])

	for (let i_panel = 0; i_panel < panels.length; ++i_panel){
	    let panel_number = panels[i_panel];
	    const panel_info = allPanelInfo[panel_num_map.get(panel_number)];
	    if (panel_info[issue] != null) {
		if (issue == 'max_erf_fit') {
		    if (panel_info[issue].length != 0) {
			passes[i_plane] += 1;
		    }
		    else {
			fails[i_plane] += 1;
		    }
		}
		else {
		    if (panel_info[issue] == true) {
			passes[i_plane] += 1;
		    }
		    if (panel_info[issue] == false) {
			fails[i_plane] += 1;
		    }
		}
	    }
	    else {
		if (issue == 'hv_test_done') { // for hv_test_done, if we have information about sparking wires etc. then we can assume the test was done even if its unknown
		    if (panel_info['high_current_wires'].length != 0 ||
			panel_info['sparking_wires'].length != 0 ||
			panel_info['short_wires'].length != 0) {
			
			passes[i_plane] += 1;
		    }
		}
	    }
	}
    }

    // Define Data
    let barwidth = 0.8/single_pan_issue_names.length;
    let offset = -(barwidth/2)*single_pan_issue_names.length + (i_issue)*(barwidth);
    single_panel_data_plane[2*i_issue] = {name : single_pan_issue_names[i_issue] + " yes",
					  x: planes,
					  y: passes,
					  mode:"markers",
					  type:"bar",
					  text: passes.map(String),
					  textposition: 'auto',
					  width : barwidth,
					  offset : offset
					 }
    single_panel_data_plane[2*i_issue+1] = {name : single_pan_issue_names[i_issue] + " no",
					    x: planes,
					    y: fails,
					    mode:"markers",
					    type:"bar",
					    text: fails.map(String),
					    textposition: 'auto',
					    base : passes,
					    width: barwidth,
					    offset : offset
					   }
}

var dead_channels_plane_data = {name : 'total',
				x: planes,
				y: n_dead_channels_plane,
				mode:"markers",
				type:"bar",
			       }

var single_channel_issue_vs_plane_plot = document.getElementById('single_channel_issue_vs_plane_plot');
var xaxis = {title : {text : 'plane number'}, tickmode : "linear", tick0 : 0.0, dtick : 1.0, gridwidth : 2};
var yaxis = {title : {text : 'no. of dead channels'}};
var layout = { title : {text: "Total Dead Channels vs Plane Number"},
	       xaxis : xaxis,
	       yaxis : yaxis,
	       scroolZoom : true,
	       barmode : 'stack',
	       shapes: [ {type: 'line', x0: 0, y0: 30.0, x1: planes.length, y1: 30.0, line:{ color: 'rgb(0, 0, 0)', width: 4, dash:'dot'} } ],
	       colorway : colors
	     };

var dead_channels_vs_plane_plot = document.getElementById('dead_channels_vs_plane_plot');
Plotly.newPlot(dead_channels_vs_plane_plot, [dead_channels_plane_data], layout);

var dead_channel_definition_plane = document.getElementById('dead_channel_definition_plane');
dead_channel_definition_plane.innerHTML = "Dead channel definition: "+dead_ch_issues.slice(0,7).join(", ") + "\n" + dead_ch_issues.slice(8).join(", ");

layout.yaxis.title.text = "Total Channels";
layout.title.text = "Single-channel QC vs Plane Number";
layout.shapes = Array()
Plotly.newPlot(single_channel_issue_vs_plane_plot, single_channel_n_data_plane, layout);

var has_data_vs_plane_plot = document.getElementById('has_data_vs_plane_plot');
var xaxis = {title : {text : 'plane number'}, tickmode : "linear", tick0 : 0.0, dtick : 1.0};
var yaxis = {title : {text : 'Number of panels in plane'}, tick0 : 0.0, dtick : 1, range : [0, 7] };

let better_grid_lines = Array(planes.length+1);
for (let i_grid_line = 0; i_grid_line < better_grid_lines.length; ++i_grid_line) {
    better_grid_lines[i_grid_line] = {type: 'line', x0: -0.5 + i_grid_line, y0: 0.0, x1: -0.5 + i_grid_line, y1: 7, line:{ color: 'rgba(0, 0, 0, 0.1)', width: 2} };
}
var layout = { title : {text: "Number of panels in plane that..."},
	       xaxis : xaxis,
	       yaxis : yaxis,
//	       barmode : 'stack',
	       scroolZoom : true,
	       shapes: better_grid_lines,
	       colorway : yes_no_colors
	     };
Plotly.newPlot(has_data_vs_plane_plot, single_panel_data_plane, layout);
