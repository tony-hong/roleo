/** Supporting for 2D visualization of WSVT **/

/*
 *  2015.12.17 Fanyu Ye
 *
 *
 *  In order for this implementation to work:
 *  Usage: Each vector should be represented by a Node element, including centroid vector
 *         Queried Word is also a Node element with needHighlight set to true
 *         All nodes should be stored in an array, in which the first element must be centroid
 *
 *         Centroid should by default at (0, 0)
 *         Input data X and Y coordinate value should be in the interval [-1, 1]
 *
 *         Invoke updateQuerySet(nodeArray) then everything should work as expected
 *
 */

/** Global Vars **/
var TRANSFORMATION;    // Transformation object
var WIDTH;             // Width of canvas
var HEIGHT;            // Height of canvas
var GLOBAL_OFFSET_X;   // Offset move origin from left-top corner to centre of the canvas
var GLOBAL_OFFSET_Y;   // Offset move origin from left-top corner to centre of the canvas
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
var startFingerDist = -1;


var isInProcessing = false;  // Boolean tells current post request is still in processing not returned yet
                             // Works only under async-request

var errCode = null;
var errCodeJSON = null;

var debugCnt = 0;

/* Default values */
var DEFAULT_NODE_RADIUS = 10;
// TODO Bellow two vars should be inited dynamically according to the data set
var MAX_MOUSE_WHEEL_CNT = 30;
var MIN_MOUSE_WHEEL_CNT = -20;

/** APIs **/
/** APIs **/
/** APIs **/

window.onresize = function() {
	reloadView();
}

function reloadView(){
	init(canvas);
	loadLastSession();
}	

function init(canvas2) {
	if (!canvas2) alert("canvas is null");
	canvas = canvas2;
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

/* Factorize initiating all state related variables out */
function initStateVariables() {
	selectedNode = null;
	isValid = false;
	isDragging = false;
	isMouseDown = false;
	isOverlap = false;
	isZoomIn = true;
	mouseWheelCnt = 0;
}

function loadErrCodeJSON(errCodeJSON_Object) {
	errCodeJSON = errCodeJSON_Object;
	if (errCodeJSON == null) alert("errCodeJSON_Object is null");
}

function createNodesFromJSON(responseJSON_Object) {
	var set = responseJSON_Object;
	if (set == null) alert("responseJSON_Object is null");
	errCode = set.errCode;
	// if error when query simply return null
	if (errCode != null) {
		return null;
	}
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
		sessionStorage.prevQuery = JSON.stringify(responseJSON_Object);
		document.getElementById("input_noun").value = sessionStorage.prevNoun;
		document.getElementById("input_verb").value = sessionStorage.prevVerb;
		document.getElementById("select_role").value = sessionStorage.prevRole;
		document.getElementById("select_model").value = sessionStorage.prevModel;
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

function draw() {
	// In processing
	if (isInProcessing) {
		drawProgressBar();
	}
	// After processing, visualize results
	else if (!isValid) {
		clear();
		// if errCode != null, display err msg
		if (errCode != null) {
			TRANSFORMATION.resetTransform();
			ctx.font = "15px Comic Sans MS";
			ctx.textAlign = "center";
			ctx.fillStyle = "red";
			ctx.fillText(errCodeJSON[errCode], 0.5*WIDTH, 0.5*HEIGHT);
			TRANSFORMATION.updateTransform();
		}
		// else
		else {
			// recompute bboxes
			for (i=0; i<view.nodeElements.length; ++i) {
				view.nodeElements[i].bbox = view.nodeElements[i].computeBBox();
			}
			// recheck grids
			// TODO check scale first, only checkGrids if scale changed
			//      with setInterval 30 for draw(), do not need addtional check, won't influence performance
			view.checkGrids(isZoomIn);
			//
			TRANSFORMATION.updateTransform();
			view.draw(ctx);
		}
		validate();
	}
}

function drawProgressBar() {
	clear();
	var date = new Date();
	var i = Math.round(2*(date.getSeconds() + date.getMilliseconds() / 1000)) % 4;
	var str = "Querying";
	for (ii=0; ii<i; ++ii) str += ".";
	for (ii=0; ii<(3-i); ++i) str += " ";
	TRANSFORMATION.resetTransform();
	ctx.font = "30px Comic Sans MS";
	ctx.textAlign = "center";
	ctx.fillStyle = "grey";
	ctx.fillText(str, 0.5*WIDTH, 0.5*HEIGHT);
	TRANSFORMATION.updateTransform();
}

function clear(bbox2D) {
	var bbox = bbox2D || new BBox2D();
	TRANSFORMATION.resetTransform();
	ctx.clearRect(bbox.pos.x, bbox.pos.y, bbox.w, bbox.h);
	//ctx.fillStyle = "black";
	//ctx.fillRect(bbox.pos.x, bbox.pos.y, bbox.w, bbox.h);
	TRANSFORMATION.updateTransform();
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

// add to window.onload
function loadView2D() {
	init(document.getElementById("myCanvas"));
	loadLastSession();
	addEventListners(canvas);
	setInterval(draw, 30);
}

function loadLastSession(){
	// load last query JSON string from session storage
	if(typeof(Storage) !== "undefined") {
		if (sessionStorage.prevQuery) {
			updateQuerySet(createNodesFromJSON(JSON.parse(sessionStorage.prevQuery)));
		}
		else {
			dummyUpdate();
		}
	} else {
		dummyUpdate();
	}
	//	
}

/** For Test Purpose **/
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

/** Models **/
/** Models **/
/** Models **/
/* Node represents a 2D projection of a queried word */
function Node(pos, word, cos, needHighlight) {
	this.pos = pos   || new Point2D();
	this.word = word || "UNDEFINED";
	this.cos = cos   || 0;
	this.needHighlight = needHighlight || false; // used for the word which get queried
}

/* Query set contains a centroid and multiple nodes */
function QuerySet(nodes) {
	this.nodes = nodes   || [];
}

function Point2D(x, y) {
	this.x = x || 0;
	this.y = y || 0;
}

/* BBox for 2D, upper-left corner is pos */
function BBox2D(pos, w, h) {
	this.pos = pos || new Point2D();
	this.w   = w   || WIDTH;
	this.h   = h   || HEIGHT;
}
BBox2D.prototype.contains = function(point2D) {
	var xMin = this.pos.x;
	var xMax = this.pos.x + this.w;
	var yMin = this.pos.y;
	var yMax = this.pos.y + this.h;
	return xMin <= point2D.x && point2D.x <= xMax &&
	       yMin <= point2D.y && point2D.y <= yMax;
}

/** Controls **/
/** Controls **/
/** Controls **/
function addEventListners(canvas) {
	// TOUCH EVENTS adapter
	// adapter should block everything and fire proper new mouse events
	canvas.addEventListener('touchstart', function(e) {
		//alert("touchstart NOT IMPLEMENTED");
		e.preventDefault();
		//
		var touches = e.touches;
		//
		if (touches.length == 1) {
			// node selection
			var mouseDownEvent = new MouseEvent('mousedown', {clientX:touches.item(0).clientX, clientY:touches.item(0).clientY});
			canvas.dispatchEvent(mouseDownEvent);
		}
	});

	canvas.addEventListener('touchmove', function(e) {
		//alert("touchmove NOT IMPLEMENTED");
		e.preventDefault();
		//
		var touches = e.touches;
		//
		if (touches.length == 1) {
			// dragging
			var mouseMoveEvent = new MouseEvent('mousemove', {clientX:touches.item(0).clientX, clientY:touches.item(0).clientY});
			canvas.dispatchEvent(mouseMoveEvent);
			//
		}
		else if (touches.length == 2) {
			//
			if (startFingerDist == -1) {
				startFingerDist = distance(touches.item(0), touches.item(1));
			}
			// zooming
			var curDist = distance(touches.item(0), touches.item(1));
			isZoomIn = (startFingerDist < curDist) ? true : false;
			var delta = 0;
			if (startFingerDist < curDist) delta = 1;
			else if (startFingerDist > curDist) delta = -1;
			// still use mouseWheelCnt to compute the scaling factor
			// same as for mouse wheel interaction
			mouseWheelCnt = Math.min(MAX_MOUSE_WHEEL_CNT, Math.max(MIN_MOUSE_WHEEL_CNT, mouseWheelCnt + delta));
			TRANSFORMATION.scale = Math.pow(1.05, mouseWheelCnt);
			invalidate();
		}
	});

	canvas.addEventListener('touchend', function(e) {
		//alert("touchend NOT IMPLEMENTED");
		e.preventDefault();
		//
		var mouseUpEvent = new MouseEvent('mouseup');
		canvas.dispatchEvent(mouseUpEvent);
	});

	// MOUSE EVENTS handler
	canvas.addEventListener('mousedown', function(e) {
		isMouseDown = true;
		preMousePos = getMouse(e);
		// codes below are dedicated for the touch interaction(node selection)
		selectedNodes = getSelectedNode(getMouse(e));
		if (selectedNodes.length != 0) {
			if (selectedNode) selectedNode.isMouseOver = false;
			selectedNode = selectedNodes[0];
			selectedNode.isMouseOver = true;
		}
		invalidate();
	});

	canvas.addEventListener('mousemove', function(e) {
		if (isMouseDown) {
			isDragging = true;
			var curMousePos = getMouse(e);
			TRANSFORMATION.translationX += curMousePos.x - preMousePos.x;
			TRANSFORMATION.translationY += curMousePos.y - preMousePos.y;
			preMousePos = curMousePos;
			invalidate();
		}
		else {
			isDragging = false;
			// clear previous state
			if (selectedNode) selectedNode.isMouseOver = false;
			//
			selectedNodes = getSelectedNode(getMouse(e));
			if (selectedNodes.length == 0) {
				selectedNode = null;
				isOverlap = false;
			}
			else if (selectedNodes.length == 1) {
				selectedNode = selectedNodes[0];
				selectedNode.isMouseOver = true;
				isOverlap = false;
			}
			else if (selectedNodes.length > 1) {
				selectedNode = selectedNodes[0];
				selectedNode.isMouseOver = true;
				isOverlap = true;
			}
			invalidate();
		}
	});

	canvas.addEventListener('mouseup', function(e) {
		isMouseDown = false;
		isDragging = false;
		startFingerDist = -1;
	});

	canvas.addEventListener('mouseout', function(e) {
		isMouseDown = false;
		isDragging = false;
		startFingerDist = -1;
	});

	canvas.addEventListener('dblclick', function(e) {
		var nodeElements = getSelectedNode(getMouse(e));
		if (nodeElements.length != 0) {
			centralize(nodeElements[0]);
			invalidate();
		}
	});

	canvas.addEventListener('wheel', function(e) {
		e.preventDefault(); // prevent browser get scrolled
		var delta = normalizeWheelSpeed(e);
		// handle wheel on overlap selection
		if (isOverlap) {
			selectedNodes = getSelectedNode(getMouse(e));
			var curIndex = 0;
			// find index if selectedNode is among the overlapped nodes, otherwise set it to first element
			if (selectedNode) {
				selectedNode.isMouseOver = false;
				for (i=0; i<selectedNodes.length; ++i) {
					if (selectedNode == selectedNodes[i]) {
						curIndex = i;
						break;
					}
				}
			}
			//
			curIndex = (curIndex + (delta > 0 ? 1 : -1)) % selectedNodes.length;
			if (curIndex < 0) curIndex = selectedNodes.length + curIndex;
			selectedNode = selectedNodes[curIndex];
			selectedNode.isMouseOver = true;
			invalidate();
			return;
		}
		// handle wheel on zooming
		isZoomIn = delta > 0 ? true : false;
		mouseWheelCnt = Math.min(MAX_MOUSE_WHEEL_CNT, Math.max(MIN_MOUSE_WHEEL_CNT, mouseWheelCnt + delta));
		var pos = getMouse(e);
		TRANSFORMATION.scale = Math.pow(1.05, mouseWheelCnt);
		// Quality of Life improvement when zoom-in and zoom-out
		if (mouseWheelCnt != MIN_MOUSE_WHEEL_CNT && mouseWheelCnt != MAX_MOUSE_WHEEL_CNT) {
			var tx = 0.15*(pos.x - 0.5*WIDTH);
			var ty = 0.15*(pos.y - 0.5*HEIGHT);
			TRANSFORMATION.translationX -= tx;
			TRANSFORMATION.translationY -= ty;
		}
		invalidate();
	});

    // fixes a problem where double clicking causes text to get selected on the canvas
    canvas.addEventListener('selectstart', function(e) { e.preventDefault(); return false; }, false);

	// add image downloader listener
	var dlBtn = document.getElementById("downloadBtn");
	if (!dlBtn) alert("getElementById(\"downloadBtn\") failed!");
	dlBtn.addEventListener('click', function(e) {
		var dlA = document.getElementById("downloadA");
		if (!dlA) alert("getElementById(\"downloadA\") failed!");
		dlA.href = canvas.toDataURL('image/jpeg');
		// TODO change name dynamically
		dlA.download = "WSVT_Result.jpeg" ;
		dlA.click();
	});;
}

/* Get the node which it's BBox contains current mouse position, return null if nothing get involved */
function getSelectedNode(mousePos) {
	var nodes = [];
	if (!mousePos) alert("arg mousePos is null");
	for (i=0; i<view.nodeElements.length; ++i) {
		var nodeElement = view.nodeElements[i];
		if (nodeElement.bbox.contains(mousePos))
			nodes.push(nodeElement);
	}
	return nodes;
}

/* Get precise mouse position, reference: http://www.html5canvastutorials.com/advanced/html5-canvas-mouse-coordinates/ */
function getMouse(e) {
    var rect = canvas.getBoundingClientRect();
	return new Point2D(e.clientX - rect.left, e.clientY - rect.top);
}

/* Get mouse wheel speed, reference: http://stackoverflow.com/questions/5527601/normalizing-mousewheel-speed-across-browsers */
function normalizeWheelSpeed(event) {
    var normalized;
    if (event.wheelDelta) {
        normalized = (event.wheelDelta % 120 - 0) == -0 ? event.wheelDelta / 120 : event.wheelDelta / 12;
    } else {
        var rawAmmount = event.deltaY ? event.deltaY : event.detail;
		normalized = -rawAmmount;
        normalized = -(rawAmmount % 3 ? rawAmmount * 10 : rawAmmount / 3);
    }
	// 2016.1.22
	// due to different internal implementations for different browsers as well as different platforms
	// below is the unified return value
    if (normalized > 0) return 1;
	else if (normalized < 0) return -1;
	else return 0;
}

/** Views **/
/** Views **/
/** Views **/

/* A NodeElement contains one Node */
function NodeElement(node) {
	if (!node) alert("arg node is null");
	this.node = node;
	this.bbox = this.computeBBox();
	this.r; this.g; this.b; this.a;
	this.computeRGBA();
	this.isMouseOver = false;
	this.ifDrawText = true;
	//alert(this.node.word + " " + rgbaToString(this.r, this.g, this.b, this.a));
}
NodeElement.prototype.computeBBox = function() {
	var ul = TRANSFORMATION.transform(new Point2D(this.node.pos.x - DEFAULT_NODE_RADIUS, this.node.pos.y + DEFAULT_NODE_RADIUS));
	return new BBox2D(ul, 2*DEFAULT_NODE_RADIUS*TRANSFORMATION.scale, 2*DEFAULT_NODE_RADIUS*TRANSFORMATION.scale);
}
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
			if (deltaX > 0 && deltaY > 0) {
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
NodeElement.prototype.draw = function(ctx) {
	// draw circle
	var a = this.isMouseOver ? 1 : this.a;
	ctx.fillStyle = rgbaToString(this.r, this.g, this.b, a);
	ctx.beginPath();
	ctx.arc(this.node.pos.x, this.node.pos.y, DEFAULT_NODE_RADIUS, 0*Math.PI, 2*Math.PI);
	ctx.closePath();
	ctx.fill();

	// draw text
	if (this.ifDrawText || this.isMouseOver) { // not draw text for nodes being in same virtual grid to avoid heavy overlapping
		TRANSFORMATION.resetTransform();
		ctx.font = "20px Comic Sans MS";
		// TODO also show difference between selectedNode and others
		//      e.g. make text larger? more distinguishable
		// TODO also mark text same color as node respectively
		//      but how to distinguish queried node then???
		ctx.fillStyle = this.node.needHighlight ? "red" : rgbaToString(this.r, this.g, this.b, a);
		ctx.textAlign = "center";
		ctx.fillText(this.node.word, this.bbox.pos.x + this.bbox.w*0.5, this.bbox.pos.y - DEFAULT_NODE_RADIUS);
		TRANSFORMATION.updateTransform();
	}

	// DEBUG BBOX
	/*
	if (this.isMouseOver) {
		ctx.fillStyle = "rgba(0,0,255,0.5)";
	}
	else ctx.fillStyle = "rgba(255,0,0,0.5)";
	TRANSFORMATION.resetTransform();
	ctx.fillRect(this.bbox.pos.x, this.bbox.pos.y, this.bbox.w, this.bbox.h);
	TRANSFORMATION.updateTransform();
	*/
}

/* A CanvasView contains all elements used to draw */
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
CanvasView.prototype.checkGrids = function(isZoomIn) {
	// default grid size when scale is 1
	// can be tuned for practical performance
	var w = WIDTH  / 10.0;
	var h = HEIGHT / 10.0;
	// grid size after scale transformation
	w = w * (1 / TRANSFORMATION.scale);
	h = h * (1 / TRANSFORMATION.scale);
	// uniform grids used to store nodeElements
	var rows = Math.ceil(HEIGHT / h) + 1;
	var cols = Math.ceil(WIDTH  / w) + 1;
	var grids = [];
	// init grids
	for (x=0; x<cols; ++x) {
		for (y=0; y<rows; ++y) {
			var nodes = []
			grids.push(nodes);
		}
	}
	// iterate over all NodeElement.node.pos
	for (i=0; i<this.nodeElements.length; ++i) {
		var nodeElement = this.nodeElements[i];
		var pos = nodeElement.node.pos;
		// TODO offset another half grid would be better?
		var x = pos.x + GLOBAL_OFFSET_X + 0.5*w;
		var y = pos.y + GLOBAL_OFFSET_Y + 0.5*h;
		var ix = Math.floor(x / w);
		var iy = Math.floor(y / h);
		var index = ix + (iy * rows);
		if (index >= grids.length) alert("out of bound array access in CanvasView.checkGrids()");
		var nodes = grids[index];
		// grid contains only current element, so draw text
		if (nodes.length == 0) {
			if (isZoomIn)
				nodeElement.ifDrawText = true;
		}
		// grid already contains another element, do not draw text
		else if (nodes.length == 1) {
			if (!isZoomIn) {
				nodeElement.ifDrawText = false;
				nodes[0].ifDrawText = false;
			}
		}
		// grid already contains other elements, do not draw text
		else {
			if (!isZoomIn)
				nodeElement.ifDrawText = false;
		}
		// push current element into the grid
		nodes.push(nodeElement);
	}
	// always draw text for the queried word
	if (this.nodeElements[1].node.needHighlight == true) {
		this.nodeElements[1].ifDrawText = true;
	}
}
CanvasView.prototype.draw = function(ctx) {
	// TODO move the selected node to the top
	//      simply draw selected node at last so it appears at the top of the canvas
	//      i.e. nodeElements[{0...N}\X]
	//           nodeElements[X] -> selected word
	// draw all nodes except for the selected node
	for (i=0; i<this.nodeElements.length; ++i) {
		var nodeElement = this.nodeElements[i];
		if (nodeElement != selectedNode)
			nodeElement.draw(ctx);
	}
	// draw selectedNode at here to simply make it always on top
	if (selectedNode) selectedNode.draw(ctx);
	// draw info if necessary
	TRANSFORMATION.resetTransform();
	ctx.textBaseline = "bottom";
	if (selectedNode) {
		ctx.font = "20px sans-serif";
		ctx.fillStyle = rgbaToString(selectedNode.r, selectedNode.g, selectedNode.b, 1);
		ctx.textAlign = "right";
		var text = selectedNode.node.word + " : cos = " + selectedNode.node.cos;
		ctx.fillText(text, WIDTH, HEIGHT);
	}
	// always draw the info for the queried word
	// if it exist
	var queriedElementNode = this.nodeElements[1];
	if (!queriedElementNode) alert("No queried word find in array[1]");
	if (queriedElementNode.node.needHighlight == true) {
		ctx.font = "20px sans-serif";
		ctx.fillStyle = "red";
		ctx.textAlign = "left";
		var text = queriedElementNode.node.word + " : cos = " + queriedElementNode.node.cos;
		ctx.fillText(text, 0, HEIGHT);
	}
	TRANSFORMATION.updateTransform();
}

/* Overlapped nodes list */

/* Transformation handle the view transformation from node 2D projection coordinate to canvas coordinate */
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

/* Utility to convert rgba value to a string */
function rgbaToString(r, g, b, a) {
	var r2 = Math.round(r * 255.0);
	var g2 = Math.round(g * 255.0);
	var b2 = Math.round(b * 255.0);
	return "rgba(" + r2.toString() + "," + g2.toString() + "," + b2.toString() + "," + a.toString() + ")";
}

/* Utility to calculate distance of two touch points */
function distance(touch1, touch2) {
	var deltaX = touch1.screenX - touch2.screenX;
	var deltaY = touch1.screenY - touch2.screenY;
	return Math.sqrt(deltaX*deltaX + deltaY*deltaY);
}
