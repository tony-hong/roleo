// url for post request
var localURL = "/view2D/query/";
var serverURL = "TODO";

var xmlHttp = new XMLHttpRequest();

xmlHttp.onstatechange = function() {
	//if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
	updateQuerySet(createNodesFromJSON(xmlHttp.response));
	//}
}

function postReq() {
    // 
	var noun = document.getElementById("input_noun").value;
	var verb = document.getElementById("input_verb").value;
	var role = document.getElementById("select_role").value;
	var checkNoun = document.getElementById("checkbox_noun").checked;
	var checkVerb = document.getElementById("checkbox_verb").checked;
	if (checkNoun == false && checkVerb == false) alert("At least one check box has to be checked");
	var isCheckNoun = checkNoun ? true : false;
	var jsonString = JSON.stringify([noun, verb, role, isCheckNoun]);

	xmlHttp.open("POST", localURL, true);
	xmlHttp.send(jsonString);
	console.log('post method success!')
}




