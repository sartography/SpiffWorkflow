/**
 * The step wire widget
 * @class StepWire
 * @namespace WireIt
 * @extends WireIt.Wire
 * @constructor
 * @param  {WireIt.Terminal}    terminal1   Source terminal
 * @param  {WireIt.Terminal}    terminal2   Target terminal
 * @param  {HTMLElement} parentEl    Container of the CANVAS tag
 * @param  {Obj}                options      Wire configuration (see options property)
 */

WireIt.StepWire = function( terminal1, terminal2, parentEl, options) {
	WireIt.StepWire.superclass.constructor.call(this, terminal1, terminal2, parentEl, options);
};


YAHOO.lang.extend(WireIt.StepWire, WireIt.Wire, {
	
	/** 
    * @property xtype
    * @description String representing this class for exporting as JSON
    * @default "WireIt.StepWire"
    * @type String
    */
   xtype: "WireIt.StepWire",
	
   /**
    * Drawing methods for arrows
    */
   draw: function() {
      var margin = [4,4];

      // Get the positions of the terminals
      var p1 = this.terminal1.getXY();
      var p2 = this.terminal2.getXY();

		
		//this.terminal1.direction[0]

      var min=[ Math.min(p1[0],p2[0])-margin[0], Math.min(p1[1],p2[1])-margin[1]];
      var max=[ Math.max(p1[0],p2[0])+margin[0], Math.max(p1[1],p2[1])+margin[1]];

      // Redimensionnement du canvas
      var lw=Math.abs(max[0]-min[0]);
      var lh=Math.abs(max[1]-min[1]);

      // Convert points in canvas coordinates
      p1[0] = p1[0]-min[0];
      p1[1] = p1[1]-min[1];
      p2[0] = p2[0]-min[0];
      p2[1] = p2[1]-min[1];

		var p3 = [ p2[0], p2[1] ];
		p2[1] = p1[1];

      this.SetCanvasRegion(min[0],min[1],lw,lh);

      var ctxt=this.getContext();

      // Draw the border
      ctxt.lineCap=this.bordercap;
      ctxt.strokeStyle=this.bordercolor;
      ctxt.lineWidth=this.width+this.borderwidth*2;
      ctxt.beginPath();
      ctxt.moveTo(p1[0],p1[1]);
      ctxt.lineTo(p2[0],p2[1]);

		ctxt.lineTo(p3[0],p3[1]);
		
      ctxt.stroke();

      // Draw the inner bezier curve
      ctxt.lineCap=this.cap;
      ctxt.strokeStyle=this.color;
      ctxt.lineWidth=this.width;
      ctxt.beginPath();

      ctxt.moveTo(p1[0],p1[1]);
      ctxt.lineTo(p2[0],p2[1]);

		ctxt.lineTo(p3[0],p3[1]);

      ctxt.stroke();
   }
	
});

