/*global YAHOO,WireIt */
/**
 * Draw an Ellipse and add an editable label
 * @class RectLabelContainer
 * @extends WireIt.Container
 * @constructor
 * @param {Object} options
 * @param {WireIt.Layer} layer
 */
WireIt.RectLabelContainer = function(options, layer) {
   WireIt.RectLabelContainer.superclass.constructor.call(this, options, layer);
};

YAHOO.lang.extend(WireIt.RectLabelContainer, WireIt.Container, {
	
	
	/** 
    * @property xtype
    * @description String representing this class for exporting as JSON
    * @default "WireIt.CanvasContainer"
    * @type String
    */
   xtype: "WireIt.CanvasContainer",

	
	/** 
    * @property className
    * @description CSS class name for the container element
    * @default ""WireIt-Container WireIt-CanvasContainer WireIt-RectLabelContainer"
    * @type String
    */
	className: "WireIt-Container WireIt-CanvasContainer WireIt-RectLabelContainer",
	
	/** 
    * @property ddHandle
    * @description (only if draggable) boolean indicating we use a handle for drag'n drop
    * @default false
    * @type Boolean
    */
	ddHandle: false,
	
	/** 
    * @property label
    * @description Label String
    * @default "not set"
    * @type String
    */
   label: "not set",

	
	/** 
    * @property width
    * @description initial width of the container
    * @default 200
    * @type Integer
    */
	width: 200,

	
	render: function() {
		
		WireIt.RectLabelContainer.superclass.render.call(this);
      
		
		this.labelField = new inputEx.InPlaceEdit({parentEl: this.bodyEl, editorField: {type: 'string'}, animColors:{from:"#FFFF99" , to:"#DDDDFF"} });
		this.labelField.setValue(this.label);

	}
	
});