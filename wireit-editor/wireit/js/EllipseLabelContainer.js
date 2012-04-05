/*global YAHOO,WireIt */
/**
 * Draw an Ellipse and add an editable label
 * @class EllipseLabelContainer
 * @extends WireIt.Container
 * @constructor
 * @param {Object} options
 * @param {WireIt.Layer} layer
 */
WireIt.EllipseLabelContainer = function(options, layer) {
   WireIt.EllipseLabelContainer.superclass.constructor.call(this, options, layer);
};

YAHOO.lang.extend(WireIt.EllipseLabelContainer, WireIt.CanvasContainer, {
	
	
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
    * @default ""WireIt-Container WireIt-CanvasContainer WireIt-EllipseLabelContainer"
    * @type String
    */
	className: "WireIt-Container WireIt-CanvasContainer WireIt-EllipseLabelContainer",
	
	/** 
    * @property label
    * @description Label String
    * @default "not set"
    * @type String
    */
   label: "not set",
	
	render: function() {
		
		WireIt.EllipseLabelContainer.superclass.render.call(this);
      
		
		this.labelField = new inputEx.InPlaceEdit({parentEl: this.bodyEl, editorField: {type: 'string'}, animColors:{from:"#FFFF99" , to:"#DDDDFF"} });
		this.labelField.setValue(this.label);
		
		this.labelField.divEl.style.position = 'absolute';
		this.labelField.divEl.style.top = '50px';
		this.labelField.divEl.style.left = '75px';
	}
	
});