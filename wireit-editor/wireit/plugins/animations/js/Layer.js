

/**
 * Layer explosing animation
 * @method clearExplode
 */
WireIt.Layer.prototype.clearExplode = function(callback, bind) {

   var center = [ Math.floor(YAHOO.util.Dom.getViewportWidth()/2),
		            Math.floor(YAHOO.util.Dom.getViewportHeight()/2)];
   var R = 1.2*Math.sqrt( Math.pow(center[0],2)+Math.pow(center[1],2));

   for(var i = 0 ; i < this.containers.length ; i++) {
       var left = parseInt(dbWire.layer.containers[i].el.style.left.substr(0,dbWire.layer.containers[i].el.style.left.length-2),10);
	    var top = parseInt(dbWire.layer.containers[i].el.style.top.substr(0,dbWire.layer.containers[i].el.style.top.length-2),10);

	    var d = Math.sqrt( Math.pow(left-center[0],2)+Math.pow(top-center[1],2) );

	    var u = [ (left-center[0])/d, (top-center[1])/d];
	    YAHOO.util.Dom.setStyle(this.containers[i].el, "opacity", "0.8");

	    var myAnim = new WireIt.util.Anim(this.containers[i].terminals, this.containers[i].el, {
           left: { to: center[0]+R*u[0] },
           top: { to: center[1]+R*u[1] },
	        opacity: { to: 0, by: 0.05},
	        duration: 3
       });
       if(i == this.containers.length-1) {
          myAnim.onComplete.subscribe(function() { this.clear(); callback.call(bind);}, this, true); 
       }
	    myAnim.animate();
   }

};