var inputNoun;
var inputVerb;
var submitBtn;
var verbRadioBtn;
var nounRadioBtn;
var labelMsgNoun;
var labelMsgVerb;

var regex_non_char = "[^(a-zA-Z)]"

// add to window.onload
function loadInputTextFilter() {
	inputNoun = document.getElementById("input_noun");
	inputVerb = document.getElementById("input_verb");
	submitBtn = document.getElementById("submitBtn");
	labelMsgNoun = document.getElementById("label_msg_noun");
	labelMsgVerb = document.getElementById("label_msg_verb");
	var tmp = document.getElementsByName("group1");
	if (tmp[0].value == "noun") { nounRadioBtn = tmp[0]; verbRadioBtn = tmp[1]; }
	else                        { nounRadioBtn = tmp[1]; verbRadioBtn = tmp[0]; }
	if (inputNoun == null) { alert("Get Element ID \"input_noun\" failed"); return; }
	if (inputVerb == null) { alert("Get Element ID \"input_verb\" failed"); return; }
	if (submitBtn == null) { alert("Get Element ID \"submitBtn\" failed"); return; }
	if (labelMsgNoun == null) { alert("Get Element ID \"label_msg_noun\" failed"); return; }
	if (labelMsgVerb == null) { alert("Get Element ID \"label_msg_verb\" failed"); return; }
	if (verbRadioBtn == null) { alert("Get Elements Name \"group1\" .value == \"verb\" failed"); return; }
	if (nounRadioBtn == null) { alert("Get Elements Name \"group1\" .value == \"noun\" failed"); return; }
	
	inputVerb.addEventListener('blur', function(e) {
		preprocess(this);
	});
	inputNoun.addEventListener('blur', function(e) {
		preprocess(this);
	});
	setInterval(main, 200);
}

function main() {
	/** reset state **/
	labelMsgNoun.innerHTML="";
	labelMsgVerb.innerHTML="";
	/** reset state **/
	
	var ifDisable = false;
	
	var verb = inputVerb.value.trim();
	var noun = inputNoun.value.trim();
	
	/** 1. Empty Check  **/
	if (verbRadioBtn.checked == true) {
		if (verb == "") {
			submitBtn.disabled = true;
			labelMsgVerb.innerHTML += "Verb input cannot be empty while \"verb selects noun\" radio button is checked\n";
			ifDisable = true;
		}
	}
	else { // nounRadioBtn.checked == true
		if (noun == "") {
			submitBtn.disabled = true;
			labelMsgNoun.innerHTML += "Noun input cannot be empty while \"noun selects verb\" radio button is checked\n";
			ifDisable = true;
		}
	}
	
	/** 2. Invalid Char Check **/
	var index_verb = verb.search(regex_non_char);
	var index_noun = noun.search(regex_non_char);
	if (index_verb > -1) {
		labelMsgVerb.innerHTML += "Invalid character for verb: \"" + verb.substring(index_verb, index_verb+1) + "\"\n";
		ifDisable = true;
	}
	if (index_noun > -1) {
		labelMsgNoun.innerHTML += "Invalid character for noun: \"" + noun.substring(index_noun, index_noun+1) + "\"\n";
		ifDisable = true;
	}
	
	// TODO add additional constraints at here
	// ...
	
	// If none of the constraints meet, enable the submit button
	if (ifDisable) { submitBtn.disabled = true; return; }
	submitBtn.disabled = false;
}

function preprocess(inputElement) {
	inputElement.value = inputElement.value.trim().toLowerCase();
}