import { single_channel_issues } from './single_channel_issues.js'
const single_ch_issues = single_channel_issues();
const doublet_channel_issues = [ ];

//
// All Panels Plot
//
const response = await fetch('allPanels');
const allPanelInfo = await response.json();
//console.log(allPanelInfo);
var single_channel_n_data = Array(single_ch_issues.length)
var panels = Array(allPanelInfo.length)
var panel_num_map = new Map();
var hv_exists = Array(allPanelInfo.length).fill(0)
var passed_earboard_test = Array(allPanelInfo.length).fill(0)
for (let i_panel = 0; i_panel < panels.length; i_panel++) {
    panels[i_panel] = allPanelInfo[i_panel]['panel_id'];
    panel_num_map.set(allPanelInfo[i_panel]['panel_id'], i_panel);
    if (allPanelInfo[i_panel]['max_erf_fit'].length != 0) {
	hv_exists[i_panel] = 1;
    }
    if (allPanelInfo[i_panel]["earboard"] == true) {
	console.log(allPanelInfo[i_panel]['earboard'])
	passed_earboard_test[i_panel] = 1;
    }
    else if (allPanelInfo[i_panel]["earboard"] == false) {
	passed_earboard_test[i_panel] = 0;
    }
    else {
	passed_earboard_test[i_panel] = -0.2;
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
var hv_data_exists = {name : "HV Data Exists?",
		      x: panels,
		      y: hv_exists,
		      mode:"markers",
		      type:"scatter"
		     }
var earboard_test = {name : "Passed Earboard Test?",
		     x: panels,
		     y: passed_earboard_test,
		     mode:"markers",
		     type:"scatter"
		    }
var xaxis = {title : {text : 'panel number'}, tickmode : "linear", tick0 : 0.0, dtick : 10.0, gridwidth : 2};
var yaxis = {title : {text : ''}, 
	     tickmode: "array",
	     tickvals: [0, 1, -0.2],
	     ticktext: ['no', 'yes', 'unknown']
	    };
var layout = { title : {text: "Yes / No / Unknown Questions"},
	       xaxis : xaxis,
	       yaxis : yaxis,
	       scroolZoom : true };
Plotly.newPlot(hv_data_vs_panel_plot, [ hv_data_exists, earboard_test ], layout);


const plane_response = await fetch('allPlanes');
const allPlaneInfo = await plane_response.json();
//console.log(allPlaneInfo)
var planes = Array(allPlaneInfo.length)
var hv_exists_plane = Array(allPlaneInfo.length).fill(0)

for (let i_plane = 0; i_plane < planes.length; i_plane++) {
    planes[i_plane] = allPlaneInfo[i_plane]['plane_id'];
    let panels = allPlaneInfo[i_plane]['panel_ids']
    for (let i_panel = 0; i_panel < panels.length; ++i_panel){
	let panel_number = panels[i_panel];
	const panel_info = allPanelInfo[panel_num_map.get(panel_number)];
//	console.log(panel_number) // uncomment to check for missing panels
	if (panel_info['max_erf_fit'].length != 0) {
	    hv_exists_plane[i_plane] += 1;
	}
    }
}
var hv_data_vs_plane_plot = document.getElementById('hv_data_vs_plane_plot');
var hv_data_exists_plane = {name : "hv_data_exists",
		      x: planes,
		      y: hv_exists_plane,
		      mode:"markers",
		      type:"scatter"
		     }
var xaxis = {title : {text : 'plane number'}, tickmode : "linear", tick0 : 0.0, dtick : 1.0, gridwidth : 2};
var yaxis = {title : {text : 'no. of panels with HV data'}, tick0 : 0.0, dtick : 1, range : [0, 6] };
var layout = { title : {text: "HV Data per Plane"},
	       xaxis : xaxis,
	       yaxis : yaxis,
	       scroolZoom : true };
Plotly.newPlot(hv_data_vs_plane_plot, [ hv_data_exists_plane ], layout);
