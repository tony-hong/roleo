var inputNoun;
var inputVerb;
var submitBtn;
var verbRadioBtn;
var nounRadioBtn;

// add to window.onload
function loadInputTextFilter() {
	inputNoun = document.getElementById("input_noun");
	inputVerb = document.getElementById("input_verb");
	submitBtn = document.getElementById("submitBtn");
	var tmp = document.getElementsByName("group1");
	if (tmp[0].value == "noun") { nounRadioBtn = tmp[0]; verbRadioBtn = tmp[1]; }
	else                        { nounRadioBtn = tmp[1]; verbRadioBtn = tmp[0]; }
	if (inputNoun == null) { alert("Get Element ID \"input_noun\" failed"); return; }
	if (inputVerb == null) { alert("Get Element ID \"input_verb\" failed"); return; }
	if (submitBtn == null) { alert("Get Element ID \"submitBtn\" failed"); return; }
	if (verbRadioBtn == null) { alert("Get Elements Name \"group1\" .value == \"verb\" failed"); return; }
	if (nounRadioBtn == null) { alert("Get Elements Name \"group1\" .value == \"noun\" failed"); return; }
	setInterval(main, 200);
}

function main() {
	if (verbRadioBtn.checked == true) {
		if (inputVerb.value == "") {
			submitBtn.disabled = true;
			return;
		}
	}
	else {
		if (inputNoun.value == "") {
			submitBtn.disabled = true;
			return;
		}
	}
	// TODO add additional constraints at here
	// ...
	
	// If none of the constraints meet, enable the submit button
	submitBtn.disabled = false;
}