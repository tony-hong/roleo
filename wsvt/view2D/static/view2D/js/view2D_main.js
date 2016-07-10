/** Initialization for view2D **/
function loadView2D() {
    init(document.getElementById("myCanvas"));
    loadLastSession();
    addEventListners(canvas);
    setInterval(draw, 30);
}