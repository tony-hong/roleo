/** canvas events registration **/
function addEventListners(canvas) {
	/** TOUCH **/
	/** TOUCH **/
	// TOUCH EVENTS adapter
	// adapter should try to block everything and only fire proper new mouse events afterwards
	canvas.addEventListener('touchstart', function(e) {
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

	/** MOUSE **/
	/** MOUSE **/
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
}

/** Utilities for event handlers **/
/* Get the node which it's BBox contains current mouse position, return null if nothing get involved */
function getSelectedNode(mousePos) {
	var nodes = [];
	if (mousePos) {
		for (i=0; i<view.nodeElements.length; ++i) {
			var nodeElement = view.nodeElements[i];
			if (nodeElement.bbox.contains(mousePos))
				nodes.push(nodeElement);
		}
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

/* Utility to calculate distance of two touch points */
function distance(touch1, touch2) {
	var deltaX = touch1.screenX - touch2.screenX;
	var deltaY = touch1.screenY - touch2.screenY;
	return Math.sqrt(deltaX*deltaX + deltaY*deltaY);
}