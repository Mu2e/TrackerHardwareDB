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
var highest_panel_id = 0;
var fe55_exists = Array(allPanelInfo.length).fill(0)
var passed_earboard_test = Array(allPanelInfo.length).fill(0)
for (let i_panel = 0; i_panel < panels.length; i_panel++) {
    panels[i_panel] = allPanelInfo[i_panel]['panel_id'];
    panel_num_map.set(allPanelInfo[i_panel]['panel_id'], i_panel);
    if (allPanelInfo[i_panel]['panel_id'] > highest_panel_id) {
	highest_panel_id = allPanelInfo[i_panel]['panel_id'];
    }
    if (allPanelInfo[i_panel]['max_erf_fit'].length != 0) {
	fe55_exists[i_panel] = 1;
    }
    if (allPanelInfo[i_panel]["earboard"] == true) {
//	console.log(allPanelInfo[i_panel]['earboard'])
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

var has_data_vs_panel_plot = document.getElementById('has_data_vs_panel_plot');
var fe55_data_exists = {name : "Fe55 Data Exists?",
		      x: panels,
		      y: fe55_exists,
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
Plotly.newPlot(has_data_vs_panel_plot, [ fe55_data_exists, earboard_test ], layout);

////
// Plane QC Summary
//

const plane_response = await fetch('allPlanes');
const allPlaneInfo = await plane_response.json();
//console.log(allPlaneInfo)
var planes = Array(allPlaneInfo.length)
var single_channel_n_data_plane = Array(single_ch_issues.length)
var fe55_exists_plane = Array(allPlaneInfo.length).fill(0)
var passed_earboard_plane = Array(allPlaneInfo.length).fill(0)
var failed_earboard_plane = Array(allPlaneInfo.length).fill(0)

for (let i_issue = 0; i_issue < single_ch_issues.length; ++i_issue) {
    var n_issue = Array(allPlaneInfo.length);
    var issue = single_ch_issues[i_issue];
//    console.log(issue)
    for (let i_plane = 0; i_plane < planes.length; i_plane++) {
	n_issue[i_plane] = 0;
	planes[i_plane] = allPlaneInfo[i_plane]['plane_id'];
	let panels = allPlaneInfo[i_plane]['panel_ids']
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

for (let i_plane = 0; i_plane < planes.length; i_plane++) {
    let panels = allPlaneInfo[i_plane]['panel_ids']

    for (let i_panel = 0; i_panel < panels.length; ++i_panel){
	let panel_number = panels[i_panel];
	const panel_info = allPanelInfo[panel_num_map.get(panel_number)];
//	console.log(panel_number) // uncomment to check for missing panels
	if (panel_info['max_erf_fit'].length != 0) {
	    fe55_exists_plane[i_plane] += 1;
	}
	if (panel_info["earboard"] == true) {
	    passed_earboard_plane[i_plane] += 1;
	}
	if (panel_info["earboard"] == false) {
	    failed_earboard_plane[i_plane] += 1;
	}
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
var fe55_data_exists_plane = {name : "...have Fe55 data",
		      x: planes,
		      y: fe55_exists_plane,
		      mode:"markers",
		      type:"bar"
		     }
var passed_earboard_test_plane = {name : "...passed earboard test",
				  x: planes,
				  y: passed_earboard_plane,
				  mode:"markers",
				  type:"bar"
				 }
var failed_earboard_test_plane = {name : "...failed earboard test",
				  x: planes,
				  y: failed_earboard_plane,
				  mode:"markers",
				  type:"bar"
				 }

var xaxis = {title : {text : 'plane number'}, tickmode : "linear", tick0 : 0.0, dtick : 1.0, gridwidth : 2};
var yaxis = {title : {text : 'Number of panels in plane'}, tick0 : 0.0, dtick : 1, range : [0, 7] };
var layout = { title : {text: "Number of panels in plane that..."},
	       xaxis : xaxis,
	       yaxis : yaxis,
	       scroolZoom : true};
Plotly.newPlot(has_data_vs_plane_plot, [ fe55_data_exists_plane, passed_earboard_test_plane, failed_earboard_test_plane ], layout);
