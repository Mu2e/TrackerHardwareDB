
const log = document.querySelector("#log");

const response = await fetch('getRawHVREADMEs');
const readme_info = await response.json();

var output = ""

for (let i_readme = 0; i_readme < readme_info.length; ++i_readme) {
    output += "+++++ BEGINNING OF " + readme_info[i_readme]['filename'] + " (last modified: " + readme_info[i_readme]['last_modified'] + ", file_id #" + readme_info[i_readme]['file_id'] + ") ++++++++++++\n";
    output += readme_info[i_readme]['text']
    output += "+++++ END OF " + readme_info[i_readme]['filename'] + " (last modified: " + readme_info[i_readme]['last_modified'] + ", file_id #" + readme_info[i_readme]['file_id'] + ") ++++++++++++\n\n";
}

document.getElementById("log").innerHTML = output;//JSON.stringify(readme_info,
//							  undefined,
//							  2);
