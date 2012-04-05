/**
 * The bezier wire widget
 * @class BezierWire
 * @namespace WireIt
 * @extends WireIt.Wire
 * @constructor
 * @param  {WireIt.Terminal}    terminal1   Source terminal
 * @param  {WireIt.Terminal}    terminal2   Target terminal
 * @param  {HTMLElement} parentEl    Container of the CANVAS tag
 * @param  {Obj}                options      Wire configuration (see options property)
 */
WireIt.BezierWire = function( terminal1, terminal2, parentEl, options) {
	WireIt.BezierWire.superclass.constructor.call(this, terminal1, terminal2, parentEl, options);
};


YAHOO.lang.extend(WireIt.BezierWire, WireIt.Wire, {
	
	/** 
    * @property xtype
    * @description String representing this class for exporting as JSON
    * @default "WireIt.BezierWire"
    * @type String
    */
   xtype: "WireIt.BezierWire",
	
	/** 
    * @property coeffMulDirection
    * @description Norm of the tangent vector at the terminals
    * @default 100
    * @type Integer
    */
	coeffMulDirection: 100,
	
	
	/**
    * Redraw the Wire
    */
   draw: function() {
   
      // Get the positions of the terminals
      var p1 = this.terminal1.getXY();
      var p2 = this.terminal2.getXY();
      
      // Coefficient multiplicateur de direction
      // 100 par defaut, si distance(p1,p2) < 100, on passe en distance/2
      var coeffMulDirection = this.coeffMulDirection;
   
   
      var distance=Math.sqrt(Math.pow(p1[0]-p2[0],2)+Math.pow(p1[1]-p2[1],2));
      if(distance < coeffMulDirection){
         coeffMulDirection = distance/2;
      }
   
      // Calcul des vecteurs directeurs d1 et d2 :
      var d1 = [this.terminal1.direction[0]*coeffMulDirection,
                this.terminal1.direction[1]*coeffMulDirection];
      var d2 = [this.terminal2.direction[0]*coeffMulDirection,
                this.terminal2.direction[1]*coeffMulDirection];

      var bezierPoints=[];
      bezierPoints[0] = p1;
      bezierPoints[1] = [p1[0]+d1[0],p1[1]+d1[1]];
      bezierPoints[2] = [p2[0]+d2[0],p2[1]+d2[1]];
      bezierPoints[3] = p2;
      var min = [p1[0],p1[1]];
      var max = [p1[0],p1[1]];
      for(var i=1 ; i<bezierPoints.length ; i++){
         var p = bezierPoints[i];
         if(p[0] < min[0]){
            min[0] = p[0];
         }
         if(p[1] < min[1]){
            min[1] = p[1];
         }
         if(p[0] > max[0]){
            max[0] = p[0];
         }
         if(p[1] > max[1]){
            max[1] = p[1];
         }
      }
      // Redimensionnement du canvas
      var margin = [4,4];
      min[0] = min[0]-margin[0];
      min[1] = min[1]-margin[1];
      max[0] = max[0]+margin[0];
      max[1] = max[1]+margin[1];
      var lw = Math.abs(max[0]-min[0]);
      var lh = Math.abs(max[1]-min[1]);

   	// Store the min, max positions to display the label later
		this.min = min;
		this.max = max;

      this.SetCanvasRegion(min[0],min[1],lw,lh);
   
      var ctxt = this.getContext();
      for(i = 0 ; i<bezierPoints.length ; i++){
         bezierPoints[i][0] = bezierPoints[i][0]-min[0];
         bezierPoints[i][1] = bezierPoints[i][1]-min[1];
      }
   
      // Draw the border
      ctxt.lineCap = this.bordercap;
      ctxt.strokeStyle = this.bordercolor;
      ctxt.lineWidth = this.width+this.borderwidth*2;
      ctxt.beginPath();
      ctxt.moveTo(bezierPoints[0][0],bezierPoints[0][1]);
      ctxt.bezierCurveTo(bezierPoints[1][0],bezierPoints[1][1],bezierPoints[2][0],bezierPoints[2][1],bezierPoints[3][0],bezierPoints[3][1]);
      ctxt.stroke();
   
      // Draw the inner bezier curve
      ctxt.lineCap = this.cap;
      ctxt.strokeStyle = this.color;
      ctxt.lineWidth = this.width;
      ctxt.beginPath();
      ctxt.moveTo(bezierPoints[0][0],bezierPoints[0][1]);
      ctxt.bezierCurveTo(bezierPoints[1][0],bezierPoints[1][1],bezierPoints[2][0],bezierPoints[2][1],bezierPoints[3][0],bezierPoints[3][1]);
      ctxt.stroke();
   }


	
});