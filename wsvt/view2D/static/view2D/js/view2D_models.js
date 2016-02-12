/** Node represents a 2D projection of a queried word
 *  @constructor
 *  @param {Point2D} pos - A {@link Point2D} object
 *  @param {string} word - A string represents a word in the semantic network
 *  @param {double} cos - A double represents the cosine value between this word(vector) and the centroid(vector)
 *  @param {boolean} needHighlight - A boolean indicates whether this Node needs to be highlighted during visualization
 */
function Node(pos, word, cos, needHighlight) {
	this.pos = pos   || new Point2D();
	this.word = word || "UNDEFINED";
	this.cos = cos   || 0;
	this.needHighlight = needHighlight || false; // used for the word which get queried
}

/** Query set contains multiple {@link Node} including centroid and queried word if it exist
 *  @constructor
 *  @param {Node[]} nodes - An array contains {@link Node} represents the query result
 */
function QuerySet(nodes) {
	this.nodes = nodes   || [];
}

/** 2D Pointer representation
 *  @constructor
 *  @param {double} x - X coordinate for a 2D point
 *  @param {double} y - Y coordinate for a 2D point 
 */
function Point2D(x, y) {
	this.x = x || 0;
	this.y = y || 0;
}

/** BBox for 2D, upper-left corner is pos
 *  @constructor
 *  @param {Point2D} pos - A point as the upper left corner of this bounding box
 *  @param {double} w - The width of the bounding box
 *  @param {double} h - The height of the bounding box
 */
function BBox2D(pos, w, h) {
	this.pos = pos || new Point2D();
	this.w   = w   || WIDTH;
	this.h   = h   || HEIGHT;
}
/** Tells whether the parameter Point2D is contained in this bounding box or not
 *  @param {Point2D} point2D - A {@link Point2D} object for contain test
 */
BBox2D.prototype.contains = function(point2D) {
	var xMin = this.pos.x;
	var xMax = this.pos.x + this.w;
	var yMin = this.pos.y;
	var yMax = this.pos.y + this.h;
	return xMin <= point2D.x && point2D.x <= xMax &&
	       yMin <= point2D.y && point2D.y <= yMax;
}