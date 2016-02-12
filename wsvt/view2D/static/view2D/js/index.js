/** Callback for window.onload to initializing index.html **/
window.onload = function() {
	loadView2D(); // view2D_main.js
	loadInputTextFilter(); // inputTextFilter.js
	// load error_code.json into frontend
	$.ajax({
		url:      'errorCodeJSON/',
		type:     'GET',
		data:     null,
		async:    true,
		success:  function(response){ loadErrCodeJSON(response);}
    });
	// slider for TOP N selection
	$('#ex1').slider({
        formatter: function(value) {
            return 'Top ' + value;
        }
    });
}

/** Callback for window.onresize to create responsive canvas **/
window.onresize = function() {
	reloadView(); // view2D.js
}

/** Callback for clicking submit button **/
function submitQuery() {
	setIsInProcessing(true);
    $.ajax({
		url:      'query/',
		type:     'POST',
		data:     $('#myDiv').serialize(),
		async:    true,
		success:  function(response){
			// only store query information if no error returned
			if (response.errCode == null) {
				sessionStorage.prevNoun = document.getElementById("input_noun").value;
				sessionStorage.prevVerb = document.getElementById("input_verb").value;
				sessionStorage.prevRole = document.getElementById("select_role").value;
				sessionStorage.prevModel = document.getElementById("select_model").value;
				group = $('input:radio:checked').val();
				sessionStorage.prevGroup = group;
			}
			// invoke APIs in view2D.js to visualize the result
			updateQuerySet(createNodesFromJSON(response));
			setIsInProcessing(false);
		}
    });
}

/** Callback for clicking download image button **/
function downloadImage() {
	var dlA = document.getElementById("downloadA");
	if (!dlA) alert("getElementById(\"downloadA\") failed!");
	dlA.href = canvas.toDataURL('image/png');
	// construct name dynamically
	if(typeof(Storage) !== "undefined") {
		var nounStr = sessionStorage.prevNoun;
		var verbStr = sessionStorage.prevVerb;
		var roleStr = sessionStorage.prevRole;
		var modelStr = sessionStorage.prevModel;
		dlA.download = verbStr + "_" + roleStr + "_" + nounStr + "_" + modelStr + ".png" ;
	}
	else { // when session storage is not supported
		dla.download = "result.png";
	}
	dlA.click();
}

/** This function starts the presentation mode of the query site **/
function start_presentation_mode() {

  // disable nav bar at the top
  document.getElementById("navigation_bar").style.display = "none";

  // disable menu bar on the left
  document.getElementById("left_menu_bar").style.display = "none";

  // make the End Presentation Mode button visible
  document.getElementById("end_presentation_mode").style.display = "inline";

  // make the Start Presentation Mode button invisible
  document.getElementById("start_presentation_mode").style.display = "none";

  // set body padding-top: 0px;
  document.body.style.paddingTop = "0px";

  // change the column classes, so that the columns which are still visible, use the new space, which the left columns leaves
  document.getElementById("canvas_column").className = "col-md-8 col-sm-7 col-xs-12 col-ld-8";
  document.getElementById("right_menu_column").className = "col-md-4 col-sm-5 col-xs-12 col-ld-4";

}

/** This function ends the presentation mode of the query site **/
function end_presentation_mode() {

  // enable nav bar at the top
  document.getElementById("navigation_bar").style.display = "inline";

  // enable menu bar on the left
  document.getElementById("left_menu_bar").style.display = "inline";

  // make the End Presentation Mode button invisible again
  document.getElementById("end_presentation_mode").style.display = "none";

  // make the Start Presentation Mode button visible again
  document.getElementById("start_presentation_mode").style.display = "inline";

  // set body padding-top: 50px;
  document.body.style.paddingTop = "50px";

  // change the column classes back, so that the columns do not use the space of the left column anymore
  document.getElementById("canvas_column").className = "col-md-7 col-sm-7 col-xs-12 col-ld-6";
  document.getElementById("right_menu_column").className = "col-md-3 col-sm-2 col-xs-12 col-ld-3";
}
