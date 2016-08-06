/** Supporting for 2D visualization of WSVT **/

/*
 *  2016.2.11
 *
 *  view2D_main.js        -> main function which starts the loop for drawing
 *  view2D_events.js      -> all canvas related events handlers
 *  view2D_draw.js        -> all drawing functions used to visualize
 *  view2D_models.js     -> all low level models(data struct class) used for visulization
 *  view2D.js(this file) -> define all variables and APIs
 *                          including two class for high level models(NodeElement, CanvasView)
 *                          including one class Transformation for drawing
 *
 *  Usage:  Communicate between backend and frontend via AJAX, the response is directly a JSON, example format is in file "response_example.json"
 *          Two consecutive calls of function updateQuerySet(createNodesFromJSON(response)) will show the queried result
 *
 *  Future Development: For changing the color mapping function for a NodeElement, simply put new implementation in the NodeElement.computeRGBA()
 *
 *  Constraints: The 2D points(in json) returned from backend should resides in unit circle to ensure this implementation work
 *               This constraint is only for CanvasView.checkGrids() to work properly
 *
*/ 

/** Global Vars **/
/** Global Vars **/
/** Global Vars **/
var CONST_NODE_RADIUS = 6;
// TODO Bellow two vars would be better to be inited dynamically according to the data set
var MAX_MOUSE_WHEEL_CNT = 80;
var MIN_MOUSE_WHEEL_CNT = -10;

var TRANSFORMATION;    // Transformation object
var WIDTH;             // Width of canvas
var HEIGHT;            // Height of canvas
var GLOBAL_OFFSET_X;   // Offset move origin from left-top corner to centre of the canvas
var GLOBAL_OFFSET_Y;   // Offset move origin from left-top corner to centre of the canvas
var DEFAULT_NODE_RADIUS = CONST_NODE_RADIUS;  // The node radius for model coordinates for computing BBox and related stuff

var canvas;            // Canvas object in index.html
var ctx;               // 2D Context object in Canvas

var querySet;          // Container stores all nodes(words) returned from a single query
var view;              // Container stores all node views responsible for draw

var isValid;           // Boolean tells should canvas redraw or not
var isDragging;        // Boolean tells whether the mouse is under dragging condition (down+move)
var isMouseDown;       // Boolean tells whether mouse button is currently down
var isOverlap;         // Boolean tells whether mouse position is over overlap zone multiple nodes
var isZoomIn;          // Boolean tells whether previous zoom event is in or out
var mouseWheelCnt;     // Scalar stores mouse wheel value similar as delta value
var selectedNode;      // The current node get focused(mouse is over)
var prevMousePos;      // Position stores mouse position of previous tick
var startFingerDist = -1; // For the purpose of supporting touch events

var isInProcessing = false;  // Boolean tells current post request is still in processing not returned yet
                             // Works only under async-request

var errCode = null;      // Store the errCode if it exists in returned response
var errCodeJSON = null;  // A json load from backend which map errCode -> errMsg
var quadrant = 0
var font = 18

//var debugCnt = 0;

/** APIs **/
/** APIs **/
/** APIs **/

/** Initialize view and try load last session if it exists
 */
function reloadView(){
    init(canvas);
    loadLastSession();
}    

/** Load the errCode:errMsg pairs from server to frontend 
 *  @param {json} errCodeJSON_Object - A json contains errCode and errMsg Pairs
 */
function loadErrCodeJSON(errCodeJSON_Object) {
    errCodeJSON = errCodeJSON_Object;
    // if (errCodeJSON == null) alert("errCodeJSON_Object is null");
}

/** Should be called using the return value of function createNodesFromJSON(json_obj) as param 
 *  @param {Node[]} nodes - An array of {@link Node} instances
 */
function updateQuerySet(nodes) {
    init(document.getElementById("myCanvas"));
    if(nodes) {
        querySet.nodes = nodes;
        // scale from [-1,1] to [-0.5*WIDTH, 0.5*WIDTH] or HEIGHT
        for (i=0; i<nodes.length; ++i) {
            nodes[i].pos.x *= 0.5*WIDTH;
            nodes[i].pos.y *= 0.5*HEIGHT;
        }
        //
        view.update();
        //
        invalidate();
    }
}

/** Should be called after query result(a JSON object) returned 
 *  @param {json} responseJSON_Object - A json contains query results, see {@link response_example.json} for detail
 *  @returns {Node[]} 
 */
function createNodesFromJSON(responseJSON_Object) {
    // var btn_start_presentation_mode = document.getElementById("start_presentation_mode");
    var btn_download = document.getElementById("downloadBtn");
    // if (btn_start_presentation_mode == null) alert("getElementById(\"start_presentation_mode\") failed");
    if (btn_download == null) alert("getElementById(\"downloadBtn\") failed");
    var set = responseJSON_Object;
    if (set == null) alert("responseJSON_Object is null");
    errCode = set.errCode;
    quadrant = set.quadrant;
    // if error when query simply return null
    if (errCode != null) {
        // btn_start_presentation_mode.disabled = true;
        btn_download.disabled = true;
        return null;
    }
    else {
        // btn_start_presentation_mode.disabled = false;
        btn_download.disabled = false;
    }
    //
    var nodes = [];
    if (quadrant == 1)
        var centeroid = new Node(new Point2D(-0.75, -0.75), "centroid", 1);
    else
        var centeroid = new Node(new Point2D(), "centroid", 1);        
    nodes.push(centeroid); // [0]

    var q = set.queried;
    if (q != null) { // handle queried == null properly
        //                                            substring remove "-n"                round to two digits
        var queried = new Node(new Point2D(q.x, q.y), q.word.substring(0,q.word.length-2), Math.round((q.cos + 0.00001) * 10000) / 10000, true);
        nodes.push(queried);   // [1]
    }
    for (i=0; i<set.nodes.length; ++i) { // [2...N]
        var e = set.nodes[i];
        //                                         substring remove "-n"                round to two digits
        nodes.push(new Node(new Point2D(e.x, e.y), e.word.substring(0,e.word.length-2), Math.round((e.cos + 0.00001) * 10000) / 10000));
    }

    return nodes;
}

/** Initialize member variables for view2D 
 *  @param {Canvas} canvasObj - A DOM object represents html canvas
 */
function init(canvasObj) {
    // if (!canvasObj) alert("canvas is null");
    canvas = canvasObj;
    setCanvasDimensions();
    ctx    = canvas.getContext('2d');
    querySet = new QuerySet();
    // move origin from upper-left corner to center of the canvas
    GLOBAL_OFFSET_X = WIDTH   * 0.5;
    GLOBAL_OFFSET_Y = HEIGHT  * 0.5;
    TRANSFORMATION = new Transformation();
    TRANSFORMATION.translationX += GLOBAL_OFFSET_X;
    TRANSFORMATION.translationY += GLOBAL_OFFSET_Y;
    //
    view = new CanvasView();
    // init state vars
    initStateVariables();
}

function setCanvasDimensions(){
    querybarwidth = document.getElementById("left_menu_bar").offsetWidth
    rightmenuwidth = document.getElementById("right_menu_column").offsetWidth
        var innerWidth = window.innerWidth;
    var innerHeight = window.innerHeight;
    var scaleW = 0.95;
    if(innerWidth <= 767){
        querybarwidth = 0;
        rightmenuwidth = 0;
    }
    var w = (window.innerWidth - querybarwidth - rightmenuwidth) * scaleW;
    var h = window.innerHeight * 0.84;
    canvas.width = w;
    canvas.height = h;
    WIDTH = w;
    HEIGHT = h;
}

/* factorize initiating all state related variables out */
function initStateVariables() {
    selectedNode = null;
    isValid = false;
    isDragging = false;
    isMouseDown = false;
    isOverlap = false;
    isZoomIn = true;
    mouseWheelCnt = 0;
}

/** Set font size
 */
function setFontSize(i) {
    font = i;
}

/** Set current canvas as invalidate
 */
function invalidate() {
    isValid = false;
}

/** Set current canvas as validate
 */
function validate() {
    isValid = true;
}

/** Set the state whether backend is processing query or not
 *  @param {boolean} b - A boolean used to set the current state
 */
function setIsInProcessing(b) {
    isInProcessing = b
    var buttons = $(".btn");
    if (!buttons) alert("getElementById \"submitBtn\" failed");
    for (var i = 0; i < buttons.length; i++) {
        buttons[i].disabled = b
    };
}

/** Get the state whether backend is processing query or not
 *  @returns {boolean}
 */
function ifInProcessing() {
    return isInProcessing;
}

function loadLastSession(){
    loadSession(-1) 
}
    
function loadSession(raw_index){
    // load last query JSON string from session storage
    if(typeof(Storage) !== "undefined") {
        if (sessionStorage.searchHistory) {
            // restore previous query history
            var histories = JSON.parse(sessionStorage.searchHistory)

            if (histories.length){
                var index = (histories.length + raw_index) % histories.length
                // alert('raw_index: '+ raw_index + '\n len: '+ histories.length + '\n index: ' + index)

                var lastQuery = histories[index]

                fillRoleList(lastQuery.model)
                chageMappingList(lastQuery.model)
                
                document.getElementById("input_noun").value = lastQuery.noun;
                document.getElementById("input_verb").value = lastQuery.verb;

                $('#select_role').val(lastQuery.role)
                $('#select_model').val(lastQuery.model);
                $('#select_quadrant').val(lastQuery.quadrant);

                var radioId = 'radio_' + lastQuery.group;
                document.getElementById(radioId).checked = true;

                $('#slider_val').text(lastQuery.slider_val);
                $('#slider').slider('value', lastQuery.slider_val)

                // restore previous query infos            
                if (lastQuery.group == 'verb'){
                    document.getElementById("lbl_noun_info").textContent = lastQuery.noun;
                    document.getElementById("lbl_verb_info").textContent = lastQuery.verb + ' (selector)';
                }
                else{
                    document.getElementById("lbl_noun_info").textContent = lastQuery.noun + ' (selector)';
                    document.getElementById("lbl_verb_info").textContent = lastQuery.verb;
                }

                document.getElementById("lbl_role_info").textContent = lastQuery.role;
                document.getElementById("lbl_model_info").textContent = lastQuery.model;
                document.getElementById("lbl_topN_info").textContent = lastQuery.slider_val;
                document.getElementById("lbl_mapping_info").textContent = lastQuery.mapping;

                updateQuerySet(createNodesFromJSON(lastQuery.query));
            }
            else{
                //TODO
            }
        }
        else {
            //dummyUpdate();
        }
    } else {
        //dummyUpdate();
    }
    //    
}


/** Move a node to center of the canvas 
 *  @param {NodeElement} nodeElement - Centralize based on this {@link NodeElement}
 */
function centralize(nodeElement) {
    // translation move the current node to the center of the canvas
    var offsetX = (0.5*WIDTH)  - (nodeElement.bbox.pos.x + nodeElement.bbox.w*0.5);
    var offsetY = (0.5*HEIGHT) - (nodeElement.bbox.pos.y + nodeElement.bbox.h*0.5);
    TRANSFORMATION.translationX += offsetX;
    TRANSFORMATION.translationY += offsetY;
}

/** Reset the view and move centroid to the centre 
 */
function resetView() {
    var centroid = view.nodeElements[0];
    if (centroid == null) return;
    // rescale then centralize
    TRANSFORMATION.scale = 1;
    centralize(centroid);
    // reset grids to show all text
    view.resetGrids();
    // reset selectedNode
    if(selectedNode) selectedNode.isMouseOver = false;
    // reset state vars
    initStateVariables();
    //
    invalidate();
}
