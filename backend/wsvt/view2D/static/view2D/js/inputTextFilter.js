var inputNoun;
var inputVerb;
var submitBtn;

// add to window.onload
function loadInputTextFilter() {
	inputNoun = document.getElementById("input_noun");
	inputVerb = document.getElementById("input_verb");
	submitBtn = document.getElementById("submitBtn");
	if (inputNoun == null) { alert("Get Element ID \"input_noun\" failed"); return; }
	if (inputVerb == null) { alert("Get Element ID \"input_verb\" failed"); return; }
	if (submitBtn == null) { alert("Get Element ID \"submitBtn\" failed"); return; }
	setInterval(main, 200);
}

function main() {
	// Neither of the input field could be empty
	if (inputNoun.value == "" || inputVerb.value == "") {
		submitBtn.disabled = true;
		return;
	}
	// TODO add additional constraints at here
	// ...
	
	// If none of the constraints meet, enable the submit button
	submitBtn.disabled = false;
}