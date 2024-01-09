///////////////////////////////
// DRAC TEST RESULT PLOT
//
const showDracButton = document.getElementById('btnShowDrac');
showDracButton.addEventListener('click', async function () {
    var drac_id = document.getElementById('drac_id').value;
    const response = await fetch('getDracTests/'+drac_id);
    const drac_info = await response.json();
    console.log(drac_info);

    drac_test_plot = document.getElementById('drac_test_plot');
    var data = Array(drac_info.length);
    for (let i_drac_test = 0; i_drac_test < drac_info.length; ++i_drac_test) {
	var this_data = {
	    name : 'panel '+drac_info[i_drac_test]['panel_id'] + " (test_id = "+drac_info[i_drac_test]['drac_test_id']+")",
	    type : 'scatter',
//	    x: wire_numbers,
	    y: drac_info[i_drac_test]['pulser_total_hv']
	};
	data[i_drac_test] = this_data;
    }

    var layout = { title : {text: "DRAC " + drac_id + " Pulser HV (total)"} }
    Plotly.newPlot(drac_test_plot, data, layout);	    
});

///////////////////////////////
// DRAC TEST TABLE
//
const dracFilter = document.getElementById('drac_filter');
dracFilter.addEventListener('keyup', async function () {
    // Declare variables
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("drac_filter");
    filter = input.value.toUpperCase();
    table = document.getElementById("drac_tests_table");
    tr = table.getElementsByTagName("TR");

    // Loop through all table rows after the headings, and hide those who don't match the search query
    for (i = 1; i < tr.length; i++) {
	td = tr[i].getElementsByTagName("TD")[1];
	if (td) {
	    txtValue = td.textContent || td.innerText;
	    if (txtValue.toUpperCase().indexOf(filter) > -1) {
		tr[i].style.display = "";
	    } else {
		tr[i].style.display = "none";
	    }
	}
    }
});

const drac_tests_response = await fetch('getDracTests/');
const drac_tests_info = await drac_tests_response.json();

const drac_test_cols_response = await fetch('getDracTestCols/');
const drac_test_cols_info = await drac_test_cols_response.json();

var cols = Array(drac_test_cols_info.length);
for (let i_col = 0; i_col < cols.length; ++i_col) {
    cols[i_col] = drac_test_cols_info[i_col].name;
}

var over_table = document.getElementById("drac_tests_table");
var table = document.createElement('TABLE');
table.border = '1';

var tableBody = document.createElement('TBODY');
table.appendChild(tableBody);

for (var i = 0; i < drac_tests_info.length+1; i++) {
    var tr = document.createElement('TR');
    tableBody.appendChild(tr);
    tr.border = '1'

    var truncate_old_and_new_vals = false;
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
	    var string_to_write = drac_tests_info[i-1][cols[j]];
	    td.appendChild(document.createTextNode(string_to_write));
	}
	tr.appendChild(td);
    }
}
over_table.appendChild(table);

////////////////////
// ROC CONFIG TABLE
//
const rocConfigFilter = document.getElementById('roc_config_filter');
rocConfigFilter.addEventListener('keyup', async function () {
    // Declare variables
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("roc_config_filter");
    filter = input.value.toUpperCase();
    table = document.getElementById("roc_configs_table");
    tr = table.getElementsByTagName("TR");

    // Loop through all table rows after the headings, and hide those who don't match the search query
    for (i = 1; i < tr.length; i++) {
	td = tr[i].getElementsByTagName("TD")[0]; // [0] = roc_config_id
	if (td) {
	    txtValue = td.textContent || td.innerText;
	    if (txtValue.toUpperCase().indexOf(filter) > -1) {
		tr[i].style.display = "";
	    } else {
		tr[i].style.display = "none";
	    }
	}
    }
});

const roc_configs_response = await fetch('getDracConfigs/roc');
const roc_configs_info = await roc_configs_response.json();

var cols = ["roc_config_id", "device_serial", "design_info", "design_ver", "back_level_ver"];

var over_table = document.getElementById("roc_configs_table");
var table = document.createElement('TABLE');
table.border = '1';

var tableBody = document.createElement('TBODY');
table.appendChild(tableBody);

for (var i = 0; i < roc_configs_info.length+1; i++) {
    var tr = document.createElement('TR');
    tableBody.appendChild(tr);
    tr.border = '1'

    var truncate_old_and_new_vals = false;
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
	    var string_to_write = roc_configs_info[i-1][cols[j]];
	    td.appendChild(document.createTextNode(string_to_write));
	}
	tr.appendChild(td);
    }
}
over_table.appendChild(table);


////////////////////
// CAL CONFIG TABLE
//
const calConfigFilter = document.getElementById('cal_config_filter');
calConfigFilter.addEventListener('keyup', async function () {
    // Declare variables
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("cal_config_filter");
    filter = input.value.toUpperCase();
    table = document.getElementById("cal_configs_table");
    tr = table.getElementsByTagName("TR");

    // Loop through all table rows after the headings, and hide those who don't match the search query
    for (i = 1; i < tr.length; i++) {
	td = tr[i].getElementsByTagName("TD")[0]; // [0] = cal_config_id
	if (td) {
	    txtValue = td.textContent || td.innerText;
	    if (txtValue.toUpperCase().indexOf(filter) > -1) {
		tr[i].style.display = "";
	    } else {
		tr[i].style.display = "none";
	    }
	}
    }
});

const cal_configs_response = await fetch('getDracConfigs/cal/');
const cal_configs_info = await cal_configs_response.json();

var cols = ["cal_config_id", "id_read", "silsig", "design_name", "checksum", "design_info", "design_ver", "back_level", "debug_info", "dsn"];

var over_table = document.getElementById("cal_configs_table");
var table = document.createElement('TABLE');
table.border = '1';

var tableBody = document.createElement('TBODY');
table.appendChild(tableBody);

for (var i = 0; i < cal_configs_info.length+1; i++) {
    var tr = document.createElement('TR');
    tableBody.appendChild(tr);
    tr.border = '1'

    var truncate_old_and_new_vals = false;
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
	    var string_to_write = cal_configs_info[i-1][cols[j]];
	    td.appendChild(document.createTextNode(string_to_write));
	}
	tr.appendChild(td);
    }
}
over_table.appendChild(table);


////////////////////
// HV CONFIG TABLE
//
const hvConfigFilter = document.getElementById('hv_config_filter');
hvConfigFilter.addEventListener('keyup', async function () {
    // Declare variables
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("hv_config_filter");
    filter = input.value.toUpperCase();
    table = document.getElementById("hv_configs_table");
    tr = table.getElementsByTagName("TR");

    // Loop through all table rows after the headings, and hide those who don't match the search query
    for (i = 1; i < tr.length; i++) {
	td = tr[i].getElementsByTagName("TD")[0]; // [0] = hv_config_id
	if (td) {
	    txtValue = td.textContent || td.innerText;
	    if (txtValue.toUpperCase().indexOf(filter) > -1) {
		tr[i].style.display = "";
	    } else {
		tr[i].style.display = "none";
	    }
	}
    }
});

const hv_configs_response = await fetch('getDracConfigs/hv/');
const hv_configs_info = await hv_configs_response.json();

var cols = ["hv_config_id", "id_read", "silsig", "design_name", "checksum", "design_info", "design_ver", "back_level", "debug_info", "dsn"];

var over_table = document.getElementById("hv_configs_table");
var table = document.createElement('TABLE');
table.border = '1';

var tableBody = document.createElement('TBODY');
table.appendChild(tableBody);

for (var i = 0; i < hv_configs_info.length+1; i++) {
    var tr = document.createElement('TR');
    tableBody.appendChild(tr);
    tr.border = '1'

    var truncate_old_and_new_vals = false;
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
	    var string_to_write = hv_configs_info[i-1][cols[j]];
	    td.appendChild(document.createTextNode(string_to_write));
	}
	tr.appendChild(td);
    }
}
over_table.appendChild(table);
