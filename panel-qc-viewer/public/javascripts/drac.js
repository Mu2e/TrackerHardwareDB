
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

var cols = ["drac_test_id", "drac_id", "panel_id", "roc_config_id"];

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

const roc_configs_response = await fetch('getDracROCConfigs/');
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
