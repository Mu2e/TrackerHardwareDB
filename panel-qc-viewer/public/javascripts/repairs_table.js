export function draw_repairs_table(repairs_table_info, over_table, add_col='') {

    var cols = ["date_uploaded", "uploaded_by", "comment", "column_changed", "old_value", "new_value"];
    if (add_col != "") {
	cols.unshift(add_col)
    }

    while (over_table.firstChild) {
	over_table.removeChild(over_table.lastChild);
    }

    var table = document.createElement('TABLE');
    table.border = '1';

    var tableBody = document.createElement('TBODY');
    table.appendChild(tableBody);

    for (var i = 0; i < repairs_table_info.length+1; i++) {
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
		var string_to_write = repairs_table_info[i-1][cols[j]];
		if (cols[j]=='column_changed') {
		    if (repairs_table_info[i-1][cols[j]]=='max_erf_fit' || repairs_table_info[i-1][cols[j]]=='rise_time') {
			truncate_old_and_new_vals = true;
		    }
		}
		else {
		    if (truncate_old_and_new_vals) {
			string_to_write = repairs_table_info[i-1][cols[j]].slice(0, 9) + " ... " + repairs_table_info[i-1][cols[j]].slice(-9) + " ";
		    }
		}
		td.appendChild(document.createTextNode(string_to_write));
	    }
	    tr.appendChild(td);
	}
    }
    over_table.appendChild(table);


}
