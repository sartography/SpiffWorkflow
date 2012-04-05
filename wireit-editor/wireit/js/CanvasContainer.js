/*global YAHOO,WireIt */
/**
 * Container that draw into a canvas. (Draw an Ellipse by default, override the drawCanvas method to customize)
 * @class CanvasContainer
 * @extends WireIt.Container
 * @constructor
 * @param {Object} options
 * @param {WireIt.Layer} layer
 */
WireIt.CanvasContainer = function(options, layer) {
   WireIt.CanvasContainer.superclass.constructor.call(this, options, layer);
};

YAHOO.lang.extend(WireIt.CanvasContainer, WireIt.Container, {
	
	/** 
    * @property xtype
    * @description String representing this class for exporting as JSON
    * @default "WireIt.CanvasContainer"
    * @type String
    */
   xtype: "WireIt.CanvasContainer",
	
	/** 
    * @property ddHandle
    * @description (only if draggable) boolean indicating we use a handle for drag'n drop
    * @default false
    * @type Boolean
    */
	ddHandle: false,
	
	/** 
    * @property className
    * @description CSS class name for the container element
    * @default ""WireIt-Container WireIt-CanvasContainer"
    * @type String
    */
	className: "WireIt-Container WireIt-CanvasContainer",
	
	/** 
    * @property width
    * @description initial width of the container
    * @default 200
    * @type Integer
    */
	width: 200,
	
	/** 
    * @property height
    * @description initial height of the container
    * @default 100
    * @type Integer
    */
	height: 100,

   
   /**
 	 * Add the image property as a background image for the container
    * @method render
    */
   render: function() {
      WireIt.CanvasContainer.superclass.render.call(this);

		this.canvasEl = new WireIt.CanvasElement(this.bodyEl);
		this.canvasEl.SetCanvasRegion(0,0, this.width, this.height );
		this.canvasWidth = this.width;
		this.canvasHeight = this.height;
		this.drawCanvas();
   },

	/**
	 * On resize, resize the canvas element and redraw it
	 */
	onResize: function(event, args) {
		
		WireIt.CanvasContainer.superclass.onResize.call(this, event, args);
		
      var size = args[0];
		
		// resize the canvas
		// TODO: do not hardcode those sizes !!
		this.canvasWidth = (size[0]-14);
		this.canvasHeight = (size[1]-( this.ddHandle ? 44 : 14) );
		this.canvasEl.SetCanvasRegion(0,0, this.canvasWidth, this.canvasHeight );
		
		this.drawCanvas();
   },
   
	/**
	 * Draw the canvas
	 */
	drawCanvas: function() {
		var ctx = this.canvasEl.getContext('2d');
	 
		ctx.strokeStyle = "#5B81AD"; 
      ctx.lineWidth= 2;

		ctx.save();
		ctx.translate( this.canvasWidth/2, this.canvasHeight/2);
		ctx.scale(this.canvasWidth/2-5, this.canvasHeight/2-5);
		ctx.arc(0, 0, 1, 0, 2*Math.PI, false);
		
		ctx.restore(); // restore so stroke() isn’t scaled
		
		ctx.stroke();
		
		ctx.fillStyle = "#DCE6F2"; 
		ctx.fill();
	}

});