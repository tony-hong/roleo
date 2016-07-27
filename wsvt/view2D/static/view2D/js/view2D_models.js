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



/** Models which encapsulate Node and querySet for visualization **/
/** Models which encapsulate Node and querySet for visualization **/
/** Models which encapsulate Node and querySet for visualization **/



/** A NodeElement contains one {@link Node}
 *  @constructor 
 *  @param {Node} node - A {@link Node} instance used to initialize
 */
function NodeElement(node, font) {
    if (!node) alert("arg node is null");
    this.node = node;
    this.bbox = this.computeBBox();
    this.r; 
    this.g; 
    this.b; 
    this.a;
    this.font = font;
    this.computeRGBA();
    this.isMouseOver = false;
    this.ifDrawText = true;
}
/** Compute the {@link BBox2D} for this instance based on the current {@link Transformation}
 */
NodeElement.prototype.computeBBox = function() {
    var ul = TRANSFORMATION.transform(new Point2D(this.node.pos.x - DEFAULT_NODE_RADIUS, this.node.pos.y + DEFAULT_NODE_RADIUS));
    return new BBox2D(ul, 2*DEFAULT_NODE_RADIUS*TRANSFORMATION.scale, 2*DEFAULT_NODE_RADIUS*TRANSFORMATION.scale);
}
/** This function initialize the RGBA value for this node element using HSL&HSV
 *  See https://en.wikipedia.org/wiki/HSL_and_HSV
 */
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
        var C = 0.8; // Saturation * Value, reference: https://en.wikipedia.org/wiki/HSL_and_HSV
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


/** Draw this instance of visualization
 *  @param {CanvasRenderingContext2D} ctx - the 2D context of the current canvas
 */
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
        ctx.font = this.font + "px Comic Sans MS";
        // TODO also show difference between selectedNode and others
        //      e.g. make text larger? more distinguishable
        // TODO also mark text same color as node respectively
        //      but how to distinguish queried node then???
        ctx.fillStyle = this.node.needHighlight ? "red" : rgbaToString(this.r, this.g, this.b, a);
        ctx.textAlign = "center";
        ctx.fillText(this.node.word, this.bbox.pos.x + this.bbox.w*0.5, this.bbox.pos.y - DEFAULT_NODE_RADIUS*TRANSFORMATION.scale);
        TRANSFORMATION.updateTransform();
    }
}

