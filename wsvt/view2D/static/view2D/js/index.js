var roleDictJSON = null
var MAX_LENGTH = 6

/** Callback for window.onload to initializing index.html **/
window.onload = function() {
  getRoleDict();

  getErrCodeJSON();

  addSlider();

  loadInputTextFilter(); // inputTextFilter.js

  loadView2D(); // view2D_main.js

  $('#select_model').change(function () {
    var currentModel = $('#select_model option:selected').val()
    if(currentModel == "TypeDM"){
      showWarningLabel('#label_warning', 'Time-consuming using TypeDM. Better with Top N<30')
    }
    fillRoleList(currentModel)
    chageMappingList(currentModel)
  });

  $('#select_history').change(function () {
    var selectedHistory = $('#select_history option:selected').val()
    clearErrMsgLabel()
    loadSession(selectedHistory)
  });

  if (!sessionStorage.searchHistory){ 
    sessionStorage.searchHistory = JSON.stringify(new Array())
    submitQuery();
  }
  else{
    var histories = JSON.parse(sessionStorage.searchHistory)
    if (histories.length == 0){
      submitQuery();
    }
    else
      fillHistories(JSON.parse(sessionStorage.searchHistory)) 
  }
}

/** Callback for window.onresize to create responsive canvas **/
window.onresize = function() {
  reloadView(); // view2D.js
}

function getRoleDict () {
  // ajax request for roleDictJSON
  if(!sessionStorage.roleDictJSON){
    $.ajax({
      url:      'roleDictJSON/',
      success:  function(response){
        loadRoleDictJSON(response)
        sessionStorage.roleDictJSON = JSON.stringify(response);

        var model = 'SDDM'
        fillRoleList(model)
        chageMappingList(model)
      }
    });
  }
  else{
    var result = JSON.parse(sessionStorage.roleDictJSON)
    loadRoleDictJSON(result)
  }
}

/** Load the roleName:roleLabel pairs from server to frontend 
 *  @param {json} roleListJSON - A json contains roleName and roleLabel Pairs
 */
function loadRoleDictJSON(json) {
  roleDictJSON = json;
  if (roleDictJSON == null) alert("roleDictJSON is null");
}

function getErrCodeJSON () {
  // ajax request for errorCodeJSON 
  if (!sessionStorage.errorCodeJSON){
    $.ajax({
      url:      'errorCodeJSON/',
      success:  function(response){
        loadErrCodeJSON(response);
        sessionStorage.errorCodeJSON = JSON.stringify(response);
      }
    });
  } 
  else {
    var result = JSON.parse(sessionStorage.errorCodeJSON)
    loadErrCodeJSON(result)
  }
}

/** Callback for clicking Submit Query button **/
function submitQuery() {
  var noun = $('#input_noun').val();
  var verb = $('#input_verb').val();
  var model = $('#select_model').val();
  
  //TODO if there is other radio boxes this may result undefined behavior
  var group = $('input[name=group1]:checked').val();
  var slider_val = $('#slider_val').text();

  var role = $('#select_role').val();
  var quadrant = $('#select_quadrant').val();
  var mapping = $('#select_quadrant option:selected').text()

  setIsInProcessing(true);

  var content = $('#myDiv').serialize()+'&top_results=' + slider_val
  $.ajax({
    url:      'query/',
    type:     'POST',
    data:     content,
    success:  function(response){

      // only store query information if no error returned
      if (response.errCode == null) {
        histories = JSON.parse(sessionStorage.searchHistory)

        record = {
          'verb'        : verb,
          'role'        : role,
          'noun'        : noun,
          'model'       : model,
          'slider_val'  : slider_val,
          'mapping'     : mapping,

          'group'       : group,
          'quadrant'    : quadrant,
          'query'       : response
        }

        histories.push(record)
        sessionStorage.searchHistory = JSON.stringify(histories)
        fillHistories(histories)
        loadLastSession();
      } 
      else {
        // Show detailed error information in a label
        setErrMsgLabel(errCodeJSON[response.errCode]);
        updateQuerySet(createNodesFromJSON(response));
      }
      // invoke APIs in view2D.js to visualize the result
      setIsInProcessing(false);
    },
    statusCode: {
      500: function(){
        setIsInProcessing(false);
        setErrMsgLabel("Internal server error. Please perform a query later.");
      },
      504: function(){
        setIsInProcessing(false);
        setErrMsgLabel("Request time out. Please refresh the page and perform another query. Try with a smaller top N.");
      }
    },
  });
}

function showWarningLabel (label, msg) {
  $(label).text(msg);
  setTimeout(function (){
    $(label).text('');
  }, 5000);
}

function showExplanation (quadrant) {
    if(quadrant < 0){
      setMsgLabel('Color of a point represents angle from vertical around centroid. ' + 
        'Distance from a point to the centroid is cosine distance.');
    } else if(quadrant == 1){
      setMsgLabel('Y-axis is cosine distance. X-axis is normalized Local Mutual Information.');
    } else {
      setMsgLabel('Distance from a point to the centroid is ' 
        + 'combination of cosine distance and normalized LMI (see Help)');
    }
}

/**
 * Show error message
 */
function setErrMsgLabel (msg) {
    // New Version: Show error message using other element out side of the canvas
    var lbl_msg_query_error = document.getElementById("label_msg_query_error");
    if (lbl_msg_query_error == null) alert("getElementById(\"label_msg_query_error\") failed");

    // TODO: change class
    lbl_msg_query_error.textContent = msg
    $('#label_msg_query_error').attr('class', 'error')
}


/**
 * Show message
 */
function setMsgLabel (msg) {
    // New Version: Show error message using other element out side of the canvas
    var lbl_msg_query_error = document.getElementById("label_msg_query_error");
    if (lbl_msg_query_error == null) alert("getElementById(\"label_msg_query_error\") failed");

    // TODO: change class
    lbl_msg_query_error.textContent = msg
    $('#label_msg_query_error').attr('class', 'msg')
}

/**
 * Clear error message 
 */
function clearErrMsgLabel () {
    var lbl_msg_query_error = document.getElementById("label_msg_query_error");
    if (lbl_msg_query_error == null) alert("getElementById(\"label_msg_query_error\") failed");
    lbl_msg_query_error.textContent = ""
}

/** Fill the roleLabel:roleName pairs to the list of drawdown box
 *  @param {str} modelName - A string contains name of the model
 */
function fillRoleList(modelName) {
  var list = $('#select_role')
  list.empty()
  var dict = eval('roleDictJSON.' + modelName)
  for (var i = 0; i < dict.length; i++) {
    var t = dict[i]
    if(modelName == 'SDDM' || modelName == 'RBE' || modelName == 'W2V')
      list.append("<option value='" + t.name + "'>" + t.name + "\t:\t" + t.label + "</option>")
    else if (modelName == 'TypeDM')
      list.append("<option value='" + t.name + "'>" + t.name + "</option>")
    else 
      alert('No such model:' + modelName)
  };
  list.val('Patient')
}

function clearHistories() {
  var list = $('#select_history')
  list.empty()
  sessionStorage.searchHistory = JSON.stringify(new Array())
}

function deleteSelected() {
  var list = $('#select_history')
  var selectedIndex = list.val()

  histories = JSON.parse(sessionStorage.searchHistory)
  histories.splice(selectedIndex, 1)
  sessionStorage.searchHistory = JSON.stringify(histories)
  fillHistories(histories)

  loadLastSession()
}

function fillHistories(histories) {
  var list = $('#select_history')
  list.empty()
  var length = histories.length

  if(length > MAX_LENGTH){
    iterLength = MAX_LENGTH
  }
  else{
    iterLength = length
  }

  for (var i = iterLength; i > 0; i--) {
    var index = length - i
    var record = histories[index]
    var text = getStringFromHistory(record)
    list.append("<option value='" + index + "'>" + text + "</option>")
  };

  list.val(length - 1)
}

function getStringFromHistory(record) {
  var text = ''
  if (record.group == 'verb'){
      text = text + record.verb + '_' + record.role[0] + '_' + record.noun
  } 
  else {
      text = text + record.noun + '_' + record.role[0] + '_' + record.verb
  }
  text = text + '_' + record.model + '_' + record.slider_val + '_' + record.mapping
  return text
}

function chageMappingList(modelName) {
  if(modelName == 'SDDM' || modelName == 'TypeDM'){
    $('.FCVM').removeAttr('disabled')
  }
  else if (modelName == 'RBE' || modelName == 'W2V'){
    $('.FCVM').attr('disabled', 'disabled')
  }  
  else 
    alert('No such model:' + modelName);
  $('#select_quadrant').val('-2')
}

/** Callback for clicking download image button **/
function downloadImage() {
  var dlA = document.getElementById("downloadA");
  if (!dlA) alert("getElementById(\"downloadA\") failed!");
  dlA.href = canvas.toDataURL('image/png');
  // construct name dynamically
  if(typeof(Storage) !== "undefined") {
    // restore previous query history
    var histories = JSON.parse(sessionStorage.searchHistory)
    var index = $('#select_history option:selected').val()
    var lastQuery = histories[index]

    var text = getStringFromHistory(lastQuery)

    dlA.download = text + ".png" ;
  }
  else { // when session storage is not supported
    dla.download = "result.png";
  }
  dlA.click();
}

function addSlider() {
  var slider_val = sessionStorage.prevTopN ? sessionStorage.prevTopN : 20;
  // alert(v)
  $('#slider').slider({
    max:    50,
    min:    6,
    step:   2,
    value:  slider_val,
    create: function(event, ui) {
      $('#slider_val').text(slider_val)
    },
    slide: function(event, ui){
      $('#slider_val').text(ui.value)
      var currentModel = $('#select_model option:selected').val()
      if(currentModel == "TypeDM" && ui.value > 30){
        showWarningLabel('#label_warning', 'Time-consuming using TypeDM. Better with Top N<30')
      }
    }
  });

  $('#font_slider').slider({
    max:    48,
    min:    14,
    step:   1,
    value:  18,
    create: function(event, ui) {
      $('#font_size').text(18)
    },
    slide: function(event, ui){
      $('#font_size').text(ui.value)
      setFontSize(ui.value)
      view.update()
    }
  });
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
  document.getElementById("right_menu_column").className = "col-md-2 col-sm-2 col-xs-12 col-ld-3";
}
