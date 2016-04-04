var roleDict;

/** Callback for window.onload to initializing index.html **/
window.onload = function() {
  select_model = sessionStorage.prevModel ? sessionStorage.prevModel : 'SDDM';

  // ajax request for roleDictJSON

  $.ajax({
    url:      'roleDictJSON/',
    type:     'GET',
    data:     null,
    async:    true,
    success:  function(response){
      loadRoleDictJSON(response, select_model);
    }
  });

  // ajax request for errorCodeJSON 
  if (!errCodeJSON){
    $.ajax({
      url:      'errorCodeJSON/',
      type:     'GET',
      data:     null,
      async:    true,
      success:  function(response){
        loadErrCodeJSON(response, select_model);
        sessionStorage.errorCodeJSON = response;
      }
    });
  }

  var slider_val = sessionStorage.prevTopN ? sessionStorage.prevTopN : 20;
  // alert(v)
  $('#slider').slider({
    max:    100,
    min:    10,
    step:   10,
    value:  slider_val,
    create: function(event, ui) {
      $('#slider-val').text(slider_val)
    },
    slide: function(event, ui){
      $('#slider-val').text(ui.value)
    }
  });

  // fillRoleList(select_model);

  loadInputTextFilter(); // inputTextFilter.js

  loadView2D(); // view2D_main.js

  if (!sessionStorage.prevVerb){ 
    setTimeout(function (){
      submitQuery();
    }, 10);
  }
}

/** Callback for window.onresize to create responsive canvas **/
window.onresize = function() {
  reloadView(); // view2D.js
}

/** Callback for clicking Submit Query button **/
function submitQuery() {
  setIsInProcessing(true);
  var slider_val= $('#slider-val').text();
  var select_model = $('#select_model').val();

  var content = $('#myDiv').serialize()+'&top_results=' + slider_val + '&select_model=' + select_model;
  $.ajax({
    url:      'query/',
    type:     'POST',
    data:     content,
    async:    true,
    success:  function(response){
      // only store query information if no error returned
      if (response.errCode == null) {
        sessionStorage.prevNoun = document.getElementById("input_noun").value;
        sessionStorage.prevVerb = document.getElementById("input_verb").value;
        sessionStorage.prevRole = document.getElementById("select_role").value;
        sessionStorage.prevModel = document.getElementById("select_model").value;
        // TODO if there is other radio boxes this may result undefined behavior
        var group = $('input[name=group1]:checked').val();
        sessionStorage.prevGroup = group;
        sessionStorage.prevTopN = $('#slider-val').text();
      }
      // invoke APIs in view2D.js to visualize the result
      updateQuerySet(createNodesFromJSON(response));
      setIsInProcessing(false);
    }
  });
}

/** Callback for clicking Change Model button **/
function changeModel() {
  setIsInProcessing(true);
  var select_model = $('#select_model').val()
  if (select_model != sessionStorage.prevModel){
    var content = $('#changingModel').serialize()
    $.ajax({
      url:      'changeModel/',
      type:     'GET',
      data:     content,
      async:    true,
      success:  function(response){
        setIsInProcessing(false);
        sessionStorage.prevModel = select_model
        fillRoleList(select_model);
        submitQuery()
      }
    });
  } else{
    setIsInProcessing(false);
  }
}

/** Load the roleName:roleLabel pairs from server to frontend 
 *  @param {json} roleListJSON - A json contains roleName and roleLabel Pairs
 */
function loadRoleDictJSON(roleDictJSON, model) {
  if (roleDictJSON == null) alert("roleDictJSON is null");
  roleDict = roleDictJSON;
  fillRoleList(model);
}

/** Fill the roleLabel:roleName pairs to the list of drawdown box
 *  @param {str} modelName - A string contains name of the model
 */
function fillRoleList (modelName) {
  var list = $('#select_role');
  list.empty();
  var dict = eval('roleDict.' + modelName);
  for (var i = 0; i < dict.length; i++) {
    var t = dict[i]
    list.append("<option value='" + t.name + "'>" + t.label + " : " + t.name + "</option>");
  };
}



/** Callback for clicking download image button **/
function downloadImage() {
	var dlA = document.getElementById("downloadA");
	if (!dlA) alert("getElementById(\"downloadA\") failed!");
	dlA.href = canvas.toDataURL('image/png');
	// construct name dynamically
	if(typeof(Storage) !== "undefined") {
		var firstStr = sessionStorage.prevVerb;
		var secondStr = sessionStorage.prevNoun;
		var roleStr = sessionStorage.prevRole;
		var modelStr = sessionStorage.prevModel;
		if (sessionStorage.prevGroup == "noun") {
			firstStr = sessionStorage.prevNoun;
			secondStr = sessionStorage.prevVerb;
		}
		dlA.download = firstStr + "_" + roleStr + "_" + secondStr + "_" + modelStr + ".png" ;
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
