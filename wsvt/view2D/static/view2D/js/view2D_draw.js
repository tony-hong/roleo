/** Loop function for canvas visualization 
 */
function draw() {
    // In processing
    if (isInProcessing) {
        drawProgressBar();
    }
    // After processing, visualize results
    else if (!isValid) {
        clear();
        // if errCode != null, display err msg
        showErrorMsg(errCode);
        // recompute bboxes
        DEFAULT_NODE_RADIUS = CONST_NODE_RADIUS/TRANSFORMATION.scale; // keep node radius irrelevant to the scale
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
        validate();
    }
}

/** Draw this instance
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
        ctx.font = "20px Comic Sans MS";
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

/** Draw all {@link NodeElement} as well as other informations on the canvas
 *  @param {CanvasRenderingContext2D} ctx - the 2D context of the current canvas
 */
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

/** Function used to compute grids adaptively to avoid showing a lot of text of nodes in a small area, 
 *  which heavily overlapping from each other 
 *  @param {boolean} isZoomIn - A boolean value indicate whether previous action is a zoom-in or not
 */
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

        // TODO ignore check
        // if (index >= grids.length) alert("out of bound array access in CanvasView.checkGrids()");

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

/** Function shows error messages 
 *  @param {string} json_errCode - A string representation as the key of an errMsg
 */
function showErrorMsg(json_errCode) {
    // Originla Version: Draw error message in canvas, but drawText do not support multiple line
/*
    TRANSFORMATION.resetTransform();
    ctx.font = "15px Comic Sans MS";
    ctx.textAlign = "center";
    ctx.fillStyle = "red";
    ctx.fillText(errCodeJSON[errCode], 0.5*WIDTH, 0.5*HEIGHT);
    TRANSFORMATION.updateTransform();
*/
    
    // Draw some message on canvas
    if (json_errCode != null) {
        var canvasMsg = "Oops ! An empty space returned."
        TRANSFORMATION.resetTransform();
        ctx.font = "15px Comic Sans MS";
        ctx.textAlign = "center";
        ctx.fillStyle = "red";
        ctx.fillText(canvasMsg, 0.5*WIDTH, 0.5*HEIGHT);
        TRANSFORMATION.updateTransform();
        // Show detailed error information in a label
        setErrMsgLabel(errCodeJSON[json_errCode]);
    }
    else {
        setErrMsgLabel("");
    }
}

function setErrMsgLabel (msg) {
    // New Version: Show error message using other element out side of the canvas
    var lbl_msg_query_error = document.getElementById("label_msg_query_error");
    if (lbl_msg_query_error == null) alert("getElementById(\"label_msg_query_error\") failed");
    lbl_msg_query_error.textContent = msg
}

/** Function draws text as feedback during querying */
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

/** Function to clear a rectangle area in canvas 
 *  @param {BBox2D} bbox2D - A {@link BBox2D} instance used for clear
 */
function clear(bbox2D) {
    var bbox = bbox2D || new BBox2D();
    TRANSFORMATION.resetTransform();
    ctx.clearRect(bbox.pos.x, bbox.pos.y, bbox.w, bbox.h);
    //ctx.fillStyle = "black";
    //ctx.fillRect(bbox.pos.x, bbox.pos.y, bbox.w, bbox.h);
    TRANSFORMATION.updateTransform();
}

/** Utility to convert rgba value to a string 
 *  @param {double} r - A double between 0 and 1 for red channel
 *  @param {double} g - A double between 0 and 1 for green channel
 *  @param {double} b - A double between 0 and 1 for blue channel
 *  @param {double} a - A double between 0 and 1 for alpha channel
 *  @returns {string} - A CSS style string represents an RGBA value, e.g. "rgba(255, 0, 0)"
 */
function rgbaToString(r, g, b, a) {
    var r2 = Math.round(r * 255.0);
    var g2 = Math.round(g * 255.0);
    var b2 = Math.round(b * 255.0);
    return "rgba(" + r2.toString() + "," + g2.toString() + "," + b2.toString() + "," + a.toString() + ")";
}