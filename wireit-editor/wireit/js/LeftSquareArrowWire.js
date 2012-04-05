/**
 * Square type of arrows for representing loops (but not restricted to) in CFG
 * @class LeftSquareArrow
 * @extends WireIt.Wire
 * @constructor
 * @param  {WireIt.Terminal}    terminal1   Source terminal
 * @param  {WireIt.Terminal}    terminal2   Target terminal
 * @param  {HTMLElement} parentEl    Container of the CANVAS tag
 * @param  {Obj}                options      Wire configuration (see options property)
 */
WireIt.LeftSquareArrow = function( terminal1, terminal2, parentEl, options) {
	WireIt.LeftSquareArrow.superclass.constructor.call(this, terminal1, terminal2, parentEl, options);
};

YAHOO.lang.extend(WireIt.LeftSquareArrow, WireIt.Wire, {
	
	/** 
    * @property xtype
    * @description String representing this class for exporting as JSON
    * @default "WireIt.LeftSquareArrow"
    * @type String
    */
   xtype: "WireIt.LeftSquareArrow",

	/**
    * Drawing method
    */
   draw: function() {	

	   // Get the positions of the terminals
	   var p1 = this.terminal1.getXY();
	   var p2 = this.terminal2.getXY();

	   var distance=Math.sqrt(Math.pow(p1[0]-p2[0],2)+Math.pow(p1[1]-p2[1],2));

		var d = 7; // arrow width/2

	   var redim = d + distance*0.5; //we have to make the canvas a little bigger because of arrows

	   var margin=[4+redim,4+redim];

	   var min=[ Math.min(p1[0],p2[0])-margin[0],
		Math.min(p1[1],p2[1])-margin[1]];

	   var max=[ Math.max(p1[0],p2[0])+margin[0],
		Math.max(p1[1],p2[1])+margin[1]];

	   // Redimensionnement du canvas
	   var lw=Math.abs(max[0]-min[0])+redim;
	   var lh=Math.abs(max[1]-min[1])+redim;

	   p1[0]=p1[0]-min[0];
	   p1[1]=p1[1]-min[1];
	   p2[0]=p2[0]-min[0];
	   p2[1]=p2[1]-min[1];

	   this.SetCanvasRegion(min[0],min[1],lw,lh);

	   var ctxt=this.getContext();

		//	  (e1) .------> * (p1)
		//   	        |
		//              |
		//	        |
		//	  (e2) .-------* (p2)

		var e1 = this.terminal1.getXY();
		var e2 = this.terminal2.getXY();
	 	e1[0] = p1[0] - distance/4 + 5;	  // Change the x coordinate; y remains same
		e1[1] = p1[1];
		e2[0] = p2[0] - distance/4 + 5;
		e2[1] = p2[1];

      // Draw the border
      ctxt.lineCap=this.bordercap;
      ctxt.strokeStyle=this.bordercolor;
      ctxt.lineWidth=this.width+this.borderwidth*2;
      ctxt.beginPath();
      ctxt.moveTo(p1[0], p1[1]);	  	
	  	ctxt.lineTo(e1[0], e1[1]);
	  	ctxt.lineTo(e2[0], e2[1]);
      ctxt.lineTo(p2[0], p2[1]);	
      ctxt.stroke();

      // Draw the inner bezier curve
      ctxt.lineCap=this.cap;
      ctxt.strokeStyle=this.color;
      ctxt.lineWidth=this.width;
      ctxt.beginPath();
      ctxt.moveTo(p1[0],p1[1]);
	  	ctxt.lineTo(e1[0], e1[1]);
	  	ctxt.lineTo(e2[0], e2[1]);
      ctxt.lineTo(p2[0], p2[1]);	
      ctxt.stroke();

	  /* start drawing arrows */
   	var t1 = e2;
   	var t2 = p2;

   	var z = [0,0]; //point on the wire with constant distance (dlug) from terminal2
   	var dlug = 20; //arrow length
   	var t = (distance === 0) ? 0 : 1-(dlug/distance);
   	z[0] = Math.abs( t1[0] +  t*(t2[0]-t1[0]) );
   	z[1] = Math.abs( t1[1] + t*(t2[1]-t1[1]) );	

   	//line which connects the terminals: y=ax+b
   	var W = t1[0] - t2[0];
   	var Wa = t1[1] - t2[1];
   	var Wb = t1[0]*t2[1] - t1[1]*t2[0];
   	if (W !== 0) {
   		a = Wa/W;
   		b = Wb/W;
   	}
   	else {
   		a = 0;
   	}

   	//line perpendicular to the main line: y = aProst*x + b
   	if (a === 0) {
   		aProst = 0;
   	}
   	else {
   		aProst = -1/a;
   	}
   	bProst = z[1] - aProst*z[0]; //point z lays on this line

   	//we have to calculate coordinates of 2 points, which lay on perpendicular line and have the same distance (d) from point z
   	var A = 1 + Math.pow(aProst,2);
   	var B = 2*aProst*bProst - 2*z[0] - 2*z[1]*aProst;
   	var C = -2*z[1]*bProst + Math.pow(z[0],2) + Math.pow(z[1],2) - Math.pow(d,2) + Math.pow(bProst,2);
   	var delta = Math.pow(B,2) - 4*A*C;

   	if (delta < 0) { return; }

   	var x1 = (-B + Math.sqrt(delta)) / (2*A);
   	var x2 = (-B - Math.sqrt(delta)) / (2*A);	
   	var y1 = aProst*x1 + bProst;
   	var y2 = aProst*x2 + bProst;

   	if(t1[1] == t2[1]) {
   	      var o = (t1[0] > t2[0]) ? 1 : -1;
      	   x1 = t2[0]+o*dlug;
      	   x2 = x1;
      	   y1 -= d;
      	   y2 += d;
   	}   	

   	//triangle fill
   	ctxt.fillStyle = this.color;
   	ctxt.beginPath();
   	ctxt.moveTo(t2[0],t2[1]);
   	ctxt.lineTo(x1,y1);
   	ctxt.lineTo(x2,y2);
   	ctxt.fill();

   	//triangle border	
   	ctxt.strokeStyle = this.bordercolor;
   	ctxt.lineWidth = this.borderwidth;
   	ctxt.beginPath();
   	ctxt.moveTo(t2[0],t2[1]);
   	ctxt.lineTo(x1,y1);
   	ctxt.lineTo(x2,y2);
   	ctxt.lineTo(t2[0],t2[1]);
   	ctxt.stroke();
   }

});


