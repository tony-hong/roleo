/** Supporting for 2D visualization of WSVT **/

/*
 *  2016.2.11
 *
 *  view2D_main.js   	 -> main function which starts the loop for drawing
 *  view2D_events.js 	 -> all canvas related events handlers
 *  view2D_draw.js   	 -> all drawing functions used to visualize
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
var CONST_NODE_RADIUS = 8;
// TODO Bellow two vars would be better to be inited dynamically according to the data set
var MAX_MOUSE_WHEEL_CNT = 30;
var MIN_MOUSE_WHEEL_CNT = -20;

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

//var debugCnt = 0;

/** APIs **/
/** APIs **/
/** APIs **/
function reloadView(){
	init(canvas);
	loadLastSession();
}	

/* load the errCode:errMsg pairs into var */
function loadErrCodeJSON(errCodeJSON_Object) {
	errCodeJSON = errCodeJSON_Object;
	if (errCodeJSON == null) alert("errCodeJSON_Object is null");
}

/* Should be called using the return value of function createNodesFromJSON(json_obj) as param */
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

/* Should be called after query result(a JSON object) returned */
function createNodesFromJSON(responseJSON_Object) {
	var btn_start_presentation_mode = document.getElementById("start_presentation_mode");
	var btn_download = document.getElementById("downloadBtn");
	if (btn_start_presentation_mode == null) alert("getElementById(\"start_presentation_mode\") failed");
	if (btn_download == null) alert("getElementById(\"downloadBtn\") failed");
	var set = responseJSON_Object;
	if (set == null) alert("responseJSON_Object is null");
	errCode = set.errCode;
	// if error when query simply return null
	if (errCode != null) {
		btn_start_presentation_mode.disabled = true;
		btn_download.disabled = true;
		return null;
	}
	else {
		btn_start_presentation_mode.disabled = false;
		btn_download.disabled = false;
	}
	//
	var nodes = [];
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
	// store JSON string into session storage
	if(typeof(Storage) !== "undefined") {
		// restore previous inputs
		sessionStorage.prevQuery = JSON.stringify(responseJSON_Object);
		document.getElementById("input_noun").value = sessionStorage.prevNoun;
		document.getElementById("input_verb").value = sessionStorage.prevVerb;
		document.getElementById("select_role").value = sessionStorage.prevRole;
		document.getElementById("select_model").value = sessionStorage.prevModel;
		radioId = 'radio_' + sessionStorage.prevGroup;
		document.getElementById(radioId).checked = true;
		// restore previous query infos
		document.getElementById("lbl_noun_info").textContent = sessionStorage.prevNoun;
		document.getElementById("lbl_verb_info").textContent = sessionStorage.prevVerb;
		document.getElementById("lbl_role_info").textContent = sessionStorage.prevRole;
		document.getElementById("lbl_model_info").textContent = sessionStorage.prevModel;
	} else {
		// Sorry! No Web Storage support..
	}
	//
	return nodes;
}

/* initialize member vars for view2D */
function init(canvasObj) {
	if (!canvasObj) alert("canvas is null");
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
	var h = window.innerHeight * 0.9;
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

function invalidate() {
	isValid = false;
}

function validate() {
	isValid = true;
}

function setIsInProcessing(b) {
	isInProcessing = b;
	var submitBtn = document.getElementById("submitBtn");
	if (!submitBtn) alert("getElementById \"submitBtn\" failed");
	if (b) submitBtn.disabled = true;
	else submitBtn.disabled = false;
}

function ifInProcessing() {
	return isInProcessing;
}

function loadLastSession(){
	// load last query JSON string from session storage
	if(typeof(Storage) !== "undefined") {
		if (sessionStorage.prevQuery) {
			updateQuerySet(createNodesFromJSON(JSON.parse(sessionStorage.prevQuery)));
		}
		else {
			//dummyUpdate();
		}
	} else {
		//dummyUpdate();
	}
	//	
}

/* Move a node to center of the canvas */
function centralize(nodeElement) {
	// translation move the current node to the center of the canvas
	var offsetX = (0.5*WIDTH)  - (nodeElement.bbox.pos.x + nodeElement.bbox.w*0.5);
	var offsetY = (0.5*HEIGHT) - (nodeElement.bbox.pos.y + nodeElement.bbox.h*0.5);
	TRANSFORMATION.translationX += offsetX;
	TRANSFORMATION.translationY += offsetY;
}

/* Reset the view and move centroid to the centre */
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

/** Models which encapsulate Node and querySet for visualization **/
/** Models which encapsulate Node and querySet for visualization **/
/** Models which encapsulate Node and querySet for visualization **/

/** A NodeElement contains one Node **/
function NodeElement(node) {
	if (!node) alert("arg node is null");
	this.node = node;
	this.bbox = this.computeBBox();
	this.r; this.g; this.b; this.a;
	this.computeRGBA();
	this.isMouseOver = false;
	this.ifDrawText = true;
}
NodeElement.prototype.computeBBox = function() {
	var ul = TRANSFORMATION.transform(new Point2D(this.node.pos.x - DEFAULT_NODE_RADIUS, this.node.pos.y + DEFAULT_NODE_RADIUS));
	return new BBox2D(ul, 2*DEFAULT_NODE_RADIUS*TRANSFORMATION.scale, 2*DEFAULT_NODE_RADIUS*TRANSFORMATION.scale);
}
/* This function initilize the rgba value for this node element, thus other color mapping method can be adapted directly in this function */
NodeElement.prototype.computeRGBA = function() {
	if (querySet.nodes.length == 0) alert("querySet is empty");
	var centeroid = querySet.nodes[0];
	var deltaX = this.node.pos.x - centeroid.pos.x;
	var deltaY = this.node.pos.y - centeroid.pos.y;
	if (deltaX == 0 && deltaY == 0) {
		this.r = 0.5;
		this.g = 0.5;
		this.b = 0.5;
		this.a = 0.5;
	}
	else {
		var H;     // Hue used to mapping Hue to RGB, reference: https://en.wikipedia.org/wiki/HSL_and_HSV
		var C = 1.0; // Saturation * Value, reference: https://en.wikipedia.org/wiki/HSL_and_HSV
		if (deltaX == 0) {
			H = deltaY > 0 ? 90.0 : 270.0;
		}
		else {
			if (deltaY == 0) {
				H = deltaX > 0 ? 360 : 180;
			}
			else if (deltaX > 0 && deltaY > 0) {
				H = Math.atan(deltaY/deltaX) / Math.PI * 180.0;
			}
			else if (deltaX < 0 && deltaY > 0) {
				H = (0.5*Math.PI + Math.atan(-deltaX/deltaY)) / Math.PI * 180.0;
			}
			else if (deltaX < 0 && deltaY < 0) {
				H = (Math.PI + Math.atan(-deltaY/-deltaX)) / Math.PI * 180.0;
			}
			else /*(deltaX > 0 && deltaY < 0)*/ {
				H = (1.5*Math.PI + Math.atan(deltaX/-deltaY)) / Math.PI * 180.0;
			}
			// mapping H to RGB, assume
			var H2 = H / 60.0;
			var X  = C * ( 1.0 - Math.abs(H2 % 2 - 1) );
			if (H2 < 1) { this.r = C; this.g = X; this.b = 0.0; }
			else if (H2 < 2) { this.r = X; this.g = C; this.b = 0.0; }
			else if (H2 < 3) { this.r = 0.0; this.g = C; this.b = X; }
			else if (H2 < 4) { this.r = 0.0; this.g = X; this.b = C; }
			else if (H2 < 5) { this.r = X; this.g = 0.0; this.b = C; }
			else if (H2 <= 6) { this.r = C; this.g = 0.0; this.b = X; }
			else alert("error when computing RGB mapping " + deltaX + ":" + deltaY + ":" + H2);
		}
		this.a = 0.5;
	}
}

/** A CanvasView contains all elements used to draw **/
function CanvasView() {
	this.nodeElements = [];
}
CanvasView.prototype.update = function() {
	if (!querySet) alert("querySet is null");
	for (i=0; i<querySet.nodes.length; ++i) {
		this.nodeElements.push(new NodeElement(querySet.nodes[i]));
	}
}
CanvasView.prototype.resetGrids = function() {
	for (i=0; i<this.nodeElements.length; ++i) {
		this.nodeElements[i].ifDrawText = true;
	}
}

/** Transformation handle the view transformation from node 2D projection coordinate to canvas(screen) coordinate **/
function Transformation() {
	this.dataScaleX = 1;    // compute based on query
	this.dataScaleY = 1;    // compute based on query
	this.scale = 1;         // compute based on moveEvent
	this.translationX = 0;  // compute based on moveEvent
	this.translationY = 0;  // compute based on moveEvent
}
/* canvas.setTransform(a,b,e,d,e,f)
 *
 *  a  b  e
 *  c  d  f
 *  0  0  1
 *
 *  Y axis get inverted
 */
Transformation.prototype.updateTransform = function() {
	ctx.setTransform(this.scale*this.dataScaleX, 0, 0, this.scale*this.dataScaleY*(-1), this.translationX, this.translationY);
}
Transformation.prototype.resetTransform = function() {
	ctx.setTransform(1,0,0,1,0,0);
}
/*  */
Transformation.prototype.transform = function(point2D) {
	return new Point2D(point2D.x * this.dataScaleX * this.scale + this.translationX,
					   point2D.y * this.dataScaleY * this.scale * (-1) + this.translationY);
}

/** For Test Purpose **/
/*
function dummyUpdate() {
	var centeroid = new Node(new Point2D(), "centroid", 1);
	var queried = new Node(new Point2D(0.515128023024, -0.853062236398), "teenager", 1, true);
	var n1 = new Node(new Point2D(0.002124, 0.011698), "i", 1);
	var n2 = new Node(new Point2D(-0.172109, -0.081946), "he", 1);
	var n3 = new Node(new Point2D(-0.330853, -0.061861), "people", 1);
	var n4 = new Node(new Point2D(0.295152, -0.322355), "child", 1);
	var n5 = new Node(new Point2D(0.578451, -0.182329), "dog", 1);
	var n6 = new Node(new Point2D(0.642296, -0.218563), "animal", 1);
	var n7 = new Node(new Point2D(0.704084, -0.132318), "bird", 1);
	var n8 = new Node(new Point2D(0.750166, -0.039185), "fish", 1);
	var n9 = new Node(new Point2D(0.510343, -0.616624), "cat", 1);
	var n10 = new Node(new Point2D(0.393059, -0.764239), "kid", 1);
	var n11 = new Node(new Point2D(0.860227, -0.025816), "disorder", 1);
	var n12 = new Node(new Point2D(0.833425, -0.242240), "lion", 1);
	var n13 = new Node(new Point2D(-0.287748, -0.827654), "man", 1);
	var n14 = new Node(new Point2D(0.803430, -0.356580), "family", 1);
	var n15 = new Node(new Point2D(0.709094, -0.519978), "rabbit", 1);
	var n16 = new Node(new Point2D(0.886305, -0.080745), "shark", 1);
	var n17 = new Node(new Point2D(0.886105, -0.125888), "cow", 1);
	var n18 = new Node(new Point2D(0.889652, -0.126101), "vegetarian", 1);
	var n19 = new Node(new Point2D(0.705012, -0.560259), "human", 1);
	var n20 = new Node(new Point2D(0.895855, -0.095523), "worm", 1);
	var nodes = [centeroid, queried, n1, n2, n3, n4, n5,
	                                 n6, n7, n8, n9, n10,
									 n11, n12, n13, n14, n15,
									 n16, n17, n18, n19, n20];
	updateQuerySet(nodes);
}
*/