/** Node represents a 2D projection of a queried word **/
function Node(pos, word, cos, needHighlight) {
	this.pos = pos   || new Point2D();
	this.word = word || "UNDEFINED";
	this.cos = cos   || 0;
	this.needHighlight = needHighlight || false; // used for the word which get queried
}

/** Query set contains a centroid and multiple nodes **/
function QuerySet(nodes) {
	this.nodes = nodes   || [];
}

/** 2D Pointer representation **/
function Point2D(x, y) {
	this.x = x || 0;
	this.y = y || 0;
}

/** BBox for 2D, upper-left corner is pos **/
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