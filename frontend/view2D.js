/** Supporting for 2D visualization of WSVT **/

/*
 *  2015.11.25 Fanyu Ye
 *
 *  In order for this implementation to work:
 *  Usage: Each vector should be represented by a Node element, including centeroid vector
 *         Queried Word is also a Node element with needHighlight set to true
 *         All nodes should be stored in an array, in which the first element must be centeroid
 *         
 *         Invoke updateQuerySet(nodeArray) then everything should work as expected
 */

/** Global Vars **/
var TRANSFORMATION;
var WIDTH;
var HEIGHT;
var canvas;
var ctx;
var querySet;
var view;
var isValid;
var isDragging;
var prevMousePos;
var mouseWheelCnt;
var selectedNode;

var debugCnt = 0;

/* Default values */
var DEFAULT_NODE_FILL   = '#AAAAAA';
var DEFAULT_NODE_RADIUS = 10;
//var MAX_NODE_RADIUS = 50;
//var MIN_NODE_RADIUS = 5;
var MAX_MOUSE_WHEEL_CNT = 10;
var MIN_MOUSE_WHEEL_CNT = -20;

/** APIs **/
/** APIs **/
/** APIs **/
function init(canvas2) {
	if (!canvas2) alert("canvas is null");
	canvas = canvas2;
	WIDTH  = canvas.width;
	HEIGHT = canvas.height;
	ctx    = canvas.getContext('2d');
	querySet = new QuerySet();
	// move origin from upper-left corner to center of the canvas
	TRANSFORMATION = new Transformation();
	TRANSFORMATION.translationX += WIDTH  * 0.5;
	TRANSFORMATION.translationY += HEIGHT * 0.5;
	//
	view = new CanvasView();
	//
	isValid = false;
	isDragging = false;
	mouseWheelCnt = 0;
}

function updateQuerySet(nodes) {
	if (!nodes) alert("nodes is null");
	init(document.getElementById("myCanvas"));
	querySet.nodes = nodes;
	// TODO scale the data set properly
	//
	view.update();
	//
	invalidate();
}

function draw() {
	if (!isValid) {
		clear();
		// recompute bboxes
		for (i=0; i<view.nodeElements.length; ++i) {
			view.nodeElements[i].bbox = view.nodeElements[i].computeBBox();
		}
		TRANSFORMATION.updateTransform();
		view.draw(ctx);
		validate();
	}
}

function clear(bbox2D) {
	var bbox = bbox2D || new BBox2D();
	TRANSFORMATION.resetTransform();
	ctx.clearRect(bbox.pos.x, bbox.pos.x, bbox.w, bbox.h);
	TRANSFORMATION.updateTransform();
}

function invalidate() {
	isValid = false;
}

function validate() {
	isValid = true;
}

window.onload = function() { 
	init(document.getElementById("myCanvas"));
	addEventListners(canvas);
	dummyUpdate();
	setInterval(draw, 30);
}

/** For Test Purpose **/
function dummyUpdate() {
	var centeroid = new Node(new Point2D(), "CENTEROID", 1);
	var node1 = new Node(new Point2D(50, 50), "NODE1", 0.5);
	var node2 = new Node(new Point2D(-50, 100), "NODE2", 0.2);
	var node3 = new Node(new Point2D(100, 75), "NODE3", 0.4);
	var node4 = new Node(new Point2D(-50, -50), "NODE4", 0.3);
	var nodes = [centeroid, node1, node2, node3, node4];
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
	canvas.addEventListener('mousedown', function(e) {
		isDragging = true;
		preMousePos = getMouse(e);
	});
	
	canvas.addEventListener('mousemove', function(e) {
		if (isDragging) {
			var curMousePos = getMouse(e);
			TRANSFORMATION.translationX += curMousePos.x - preMousePos.x;
			TRANSFORMATION.translationY += curMousePos.y - preMousePos.y;
			preMousePos = curMousePos;
			invalidate();
		}
		else {
			// clear previous state
			if (selectedNode) selectedNode.isMouseOver = false;
			//
			selectedNode = getSelectedNode(getMouse(e));
			if (selectedNode) {
				selectedNode.isMouseOver = true;
			}
			invalidate();
		}
	});
	
	canvas.addEventListener('mouseup', function(e) {
		isDragging = false;
	});
	
	canvas.addEventListener('mouseout', function(e) {
		isDragging = false;
	});
	
	canvas.addEventListener('dblclick', function(e) {
		var nodeElement = getSelectedNode(getMouse(e));
		if (nodeElement) {
			// translation move the current node to the center of the canvas
			var offsetX = (0.5*WIDTH)  - (nodeElement.bbox.pos.x + nodeElement.bbox.w*0.5);
			var offsetY = (0.5*HEIGHT) - (nodeElement.bbox.pos.y + nodeElement.bbox.h*0.5);
			TRANSFORMATION.translationX += offsetX;
			TRANSFORMATION.translationY += offsetY;
			invalidate();
		}
	});
	
	canvas.addEventListener('wheel', function(e) {
		e.preventDefault(); // prevent browser get scrolled
		mouseWheelCnt = Math.min(MAX_MOUSE_WHEEL_CNT, Math.max(MIN_MOUSE_WHEEL_CNT, mouseWheelCnt + normalizeWheelSpeed(e)));
		TRANSFORMATION.scale = Math.pow(1.05, mouseWheelCnt);
		invalidate();
	});
	
    //fixes a problem where double clicking causes text to get selected on the canvas
    //canvas.addEventListener('selectstart', function(e) { e.preventDefault(); return false; }, false);
}

/* Get the node which it's BBox contains current mouse position, return null if nothing get involved */
function getSelectedNode(mousePos) {
	if (!mousePos) alert("arg mousePos is null");
	for (i=0; i<view.nodeElements.length; ++i) {
		var nodeElement = view.nodeElements[i];
		if (nodeElement.bbox.contains(mousePos))
			return nodeElement;
	}
	return null;
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
        normalized = -(rawAmmount % 3 ? rawAmmount * 10 : rawAmmount / 3);
    }
    return normalized;
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
			else if (H2 < 6) { this.r = C; this.g = 0.0; this.b = X; }
			else alert("error when computing RGB mapping");
		}
		this.a = 0.5;
	}
}
NodeElement.prototype.draw = function(ctx) {

	// TODO distinguish prototypical words, centeroid and queried word
	// draw circle
	var a = this.isMouseOver ? 1 : this.a;
	ctx.fillStyle = rgbaToString(this.r, this.g, this.b, a);
	ctx.beginPath();
	ctx.arc(this.node.pos.x, this.node.pos.y, DEFAULT_NODE_RADIUS, 0*Math.PI, 2*Math.PI);
	ctx.closePath();
	ctx.fill();
	
	// draw text
	TRANSFORMATION.resetTransform();
	ctx.font = "20px Comic Sans MS";
	ctx.fillStyle = "grey";
	ctx.textAlign = "center";
	ctx.fillText(this.node.word, this.bbox.pos.x + this.bbox.w*0.5, this.bbox.pos.y - 10);
	TRANSFORMATION.updateTransform();
	
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
CanvasView.prototype.draw = function(ctx) {
	// draw all nodes
	for (i=0; i<this.nodeElements.length; ++i) {
		this.nodeElements[i].draw(ctx);
	}
	// draw info if necessary
	if (selectedNode) {
		TRANSFORMATION.resetTransform();
		ctx.font = "20px sans-serif";
		ctx.fillStyle = "grey";
		ctx.textAlign = "right";
		var text = "cos = " + selectedNode.node.cos;
		ctx.fillText(text, WIDTH, HEIGHT);
		TRANSFORMATION.updateTransform();
	}
}

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

/* Utility to convert rgba value to a string */
function rgbaToString(r, g, b, a) {
	var r2 = Math.round(r * 255.0);
	var g2 = Math.round(g * 255.0);
	var b2 = Math.round(b * 255.0);
	return "rgba(" + r2.toString() + "," + g2.toString() + "," + b2.toString() + "," + a.toString() + ")";
}