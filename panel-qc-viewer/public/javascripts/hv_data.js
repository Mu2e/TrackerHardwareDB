const showAnaHVDataButton = document.getElementById('btnShowAnaHVData');
showAnaHVDataButton.addEventListener('click', async function () {
    var output = "";
    var panel_number = parseInt(document.getElementById('panel_number_ana').value);

    const max_run_to_try = 10;
    const min_run_to_try = 1;
    if (!isNaN(panel_number)) {
	var this_title = "Panel "+panel_number;
	console.log(this_title);

	// Some images have a run number in the file name (e.g. mn251_r7.png, mn251_r7_smooth.png)
	var i_smooth_run = max_run_to_try;
	var img_smoothdata = document.getElementById('img_smoothdata');
	var smooth_data = function(){ 
	    if (i_smooth_run == 1) {
		img_smoothdata.src =  "images/hv_data/mn" + panel_number.toString().padStart(3,'0') + "_datasmooth.png";
		--i_smooth_run;
	    }
	    else if (i_smooth_run > min_run_to_try) {
		img_smoothdata.src =  "images/hv_data/mn" + panel_number.toString().padStart(3,'0') + "_r" + i_smooth_run.toString() + "_smooth.png";
		--i_smooth_run;
	    }
	    else {
		img_smoothdata.src = "images/hv_data/notfound.png";
	    }
	}
	img_smoothdata.onerror = smooth_data;
	img_smoothdata.onload = function() { document.getElementById("smooth_filename").innerHTML = img_smoothdata.src; }
	smooth_data();
	
	var i_raw_run = max_run_to_try;
	var img_rawdata = document.getElementById('img_rawdata');
	var raw_data = function(){ 
	    if (i_raw_run == 1) {
		img_rawdata.src =  "images/hv_data/mn" + panel_number.toString().padStart(3,'0') + "_rawdata.png";
		--i_raw_run;
	    }
	    else if (i_raw_run > min_run_to_try) {
		img_rawdata.src =  "images/hv_data/mn" + panel_number.toString().padStart(3,'0') + "_r" + i_raw_run.toString() + ".png";
		--i_raw_run;
	    }
	    else {
		img_rawdata.src = "images/hv_data/notfound.png";
	    }
	}
	img_rawdata.onerror = raw_data;
	img_rawdata.onload = function() { document.getElementById("raw_filename").innerHTML = img_rawdata.src; }
	raw_data();

	var i_maxerf_run = max_run_to_try;
	var img_maxerf = document.getElementById('img_maxerf');
	var maxerf_data = function(){ 
	    if (i_maxerf_run == 1) {
		img_maxerf.src =  "images/hv_data/mn" + panel_number.toString().padStart(3,'0') + "_maxerf.png";
		--i_maxerf_run;
	    }
	    else if (i_maxerf_run > min_run_to_try) {
		img_maxerf.src =  "images/hv_data/mn" + panel_number.toString().padStart(3,'0') + "_maxerf_r" + i_maxerf_run.toString() + ".png";
		--i_maxerf_run;
	    }
	    else {
		img_maxerf.src = "images/hv_data/notfound.png";
	    }
	}
	img_maxerf.onerror = maxerf_data;
	img_maxerf.onload = function() { document.getElementById("maxerf_filename").innerHTML = img_maxerf.src; }
	maxerf_data();
	
	var i_deltatime_run = max_run_to_try;
	var img_deltatime = document.getElementById('img_deltatime');
	var deltatime_data = function(){ 
	    if (i_deltatime_run == 1) {
		img_deltatime.src =  "images/hv_data/mn" + panel_number.toString().padStart(3,'0') + "_deltatime.png";
		--i_deltatime_run;
	    }
	    else if (i_deltatime_run > min_run_to_try) {
		img_deltatime.src =  "images/hv_data/mn" + panel_number.toString().padStart(3,'0') + "_deltatime_r" + i_deltatime_run.toString() + ".png";
		--i_deltatime_run;
	    }
	    else {
		img_deltatime.src = "images/hv_data/notfound.png";
	    }
	}
	img_deltatime.onerror = deltatime_data;
	img_deltatime.onload = function() { document.getElementById("deltatime_filename").innerHTML = img_deltatime.src; }
	deltatime_data();
    }
    else {
	output = "Input must be a number";
    }
	    

    // Now make a plot of all the previous max_erf_fit and rise_time data that is in the repairs table

    var all_wires = Array(96).fill(0)
    var wire_numbers = Array(96).fill(0)
    for (let i = 0; i < all_wires.length; i++) {
	wire_numbers[i] = i;
    }

    if (!isNaN(panel_number)) {
	const response = await fetch('getPanel/'+panel_number);
	const panel_info = await response.json();

	const repairs_table_response = await fetch('getPanelRepairs/'+panel_number);
	const repairs_table_info = await repairs_table_response.json();

	// get the old max_erf_fit and rise_time_data
	var old_max_erf_data = [];
	var old_rise_time_data = [];
	var old_filenames = [];
	for (let i_repair = 0; i_repair < repairs_table_info.length; ++i_repair) {
	    if (repairs_table_info[i_repair]['column_changed'] == 'max_erf_fit'){
		var string_to_parse = repairs_table_info[i_repair]['old_value'].replace('{','').replace('}','')
		old_max_erf_data.push(JSON.parse("[" + string_to_parse + "]")); // data stored as a string so split it
	    }
	    if (repairs_table_info[i_repair]['column_changed'] == 'rise_time'){
		var string_to_parse = repairs_table_info[i_repair]['old_value'].replace('{','').replace('}','')
		old_rise_time_data.push(JSON.parse("[" + string_to_parse + "]")); // data stored as a string so split it
	    }
	    if (repairs_table_info[i_repair]['column_changed'] == 'maxerf_risetime_filenames'){
		old_filenames.push(repairs_table_info[i_repair]['old_value']);
	    }
	}
	
	var this_panel_info = panel_info[0]
	var doublet_numbers = Array(48).fill(0)
	for (let i = 0; i < doublet_numbers.length; i++) {
	    doublet_numbers[i] = (2*i+0.5);
	}

	var all_max_erf_data = Array(old_max_erf_data.length + 1) // +1 for current data
	var max_erf_fits = this_panel_info['max_erf_fit'];
	var max_erf_fit_data = {
	    name : JSON.stringify(this_panel_info['maxerf_risetime_filenames']),
	    type : 'scatter',
	    x: doublet_numbers,
	    y: max_erf_fits,
	    mode : 'lines+markers'
	};	    
	all_max_erf_data[0] = max_erf_fit_data;
	for (let i_data = 0; i_data < old_max_erf_data.length; ++i_data) {
	    var this_data = { name : old_filenames[i_data],
			      type : 'scatter',
			      x : doublet_numbers,
			      y : old_max_erf_data[i_data],
			      mode : 'lines+markers'
			    }
	    all_max_erf_data[i_data+1] = this_data;
	}

	var xaxis = {title : {text : 'straw number'}, tickmode : "linear", tick0 : 0.0, dtick : 1.0, gridwidth : 2, range : [-0.5, 96.5]};
	var yaxis = {title: {text : 'Max Erf Fit [nA]'}, tickmode : "linear", tick0 : 0.0, dtick : 0.2, gridwidth : 2, range : [-0.2, 1.2]};
	var layout = { title : {text: this_title + " Max Erf Fit"},
		       xaxis : xaxis,
		       yaxis : yaxis,
//		       barmode : 'stack',
		       legend: {"orientation": "h"},
		       //		   margin: {t:0},
		       scroolZoom : true }; 

	max_erf_history_plot = document.getElementById('max_erf_history_plot');
	Plotly.newPlot(max_erf_history_plot, all_max_erf_data, layout);	    

	var all_rise_time_data = Array(old_rise_time_data.length + 1) // +1 for current data
	var rise_times = this_panel_info['rise_time'];
	var rise_time_data = {
	    name : JSON.stringify(this_panel_info['maxerf_risetime_filenames']),
	    type : 'scatter',
	    x: doublet_numbers,
	    y: rise_times,
	    mode : 'lines+markers'
	};	    
	all_rise_time_data[0] = rise_time_data;
	for (let i_data = 0; i_data < old_rise_time_data.length; ++i_data) {
	    var this_data = { name : old_filenames[i_data],
			      type : 'scatter',
			      x : doublet_numbers,
			      y : old_rise_time_data[i_data],
			      mode : 'lines+markers'
			    }
	    all_rise_time_data[i_data+1] = this_data;
	}

	var xaxis = {title : {text : 'straw number'}, tickmode : "linear", tick0 : 0.0, dtick : 1.0, gridwidth : 2, range : [-0.5, 96.5]};
	var yaxis = {title: {text : 'Rise Time [min]'}, tickmode : "linear", tick0 : 0.0, dtick : 10, gridwidth : 2, range : [0, 60]};
	var layout = { title : {text: this_title + " Max Erf Fit"},
		       xaxis : xaxis,
		       yaxis : yaxis,
//		       barmode : 'stack',
		       legend: {"orientation": "h"},
		       //		   margin: {t:0},
		       scroolZoom : true }; 

	rise_time_history_plot = document.getElementById('rise_time_history_plot');
	Plotly.newPlot(rise_time_history_plot, all_rise_time_data, layout);	    

    }

    // Now do the table of raw data file names and tarball locations
    var cols = ["filename", "first_timestamp", "last_timestamp", "tarball", "comment"]
    if (!isNaN(panel_number)) {
	var this_title = "Panel "+panel_number;

	const hv_table_response = await fetch('getRawHVTable/'+panel_number);
	const hv_table = await hv_table_response.json();
//	console.log(hv_table)
	var over_table = document.getElementById("raw_hv_files_table");

	// Remove the old table first
//	var old_table = document.getElementById('TABLE');
//	if (old_table) {
//	    over_table.removeChild(old_table);
//	}
	while (over_table.firstChild) {
	    over_table.removeChild(over_table.lastChild);
	}

	var table = document.createElement('TABLE');
	table.border = '1';

	var tableBody = document.createElement('TBODY');
	table.appendChild(tableBody);

	for (var i = 0; i < hv_table.length+1; i++) {
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
		    td.appendChild(document.createTextNode(hv_table[i-1][cols[j]]));
		}
		tr.appendChild(td);
	    }
	}
	over_table.appendChild(table);
    }
    else {
	output = "Input must be a number";
    }
	    
//    document.getElementById("panel_info").innerHTML = output;
});
