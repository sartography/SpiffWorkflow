/*global YAHOO,WireIt,window */
/**
 * A layer encapsulate a bunch of containers and wires
 * @class Layer
 * @namespace WireIt
 * @constructor
 * @param {Object}   options   Configuration object (see the properties)
 */
WireIt.Layer = function(options) {
   
   this.setOptions(options);
   
   /**
    * List of all the WireIt.Container (or subclass) instances in this layer
    * @property containers
    * @type {Array}
    */
   this.containers = [];
   
   /**
    * List of all the WireIt.Wire (or subclass) instances in this layer
    * @property wires
    * @type {Array}
    */
   this.wires = [];
   
	/**
	 * TODO
	 */
   this.groups = [];
   
   /**
    * Layer DOM element
    * @property el
    * @type {HTMLElement}
    */
   this.el = null;

	/**
    * Event that is fired when the layer has been changed
    * You can register this event with myTerminal.eventChanged.subscribe(function(e,params) { }, scope);
    * @event eventChanged
    */
   this.eventChanged = new YAHOO.util.CustomEvent("eventChanged");
   
   /**
    * Event that is fired when a wire is added
    * You can register this event with myTerminal.eventAddWire.subscribe(function(e,params) { var wire=params[0];}, scope);
    * @event eventAddWire
    */
   this.eventAddWire = new YAHOO.util.CustomEvent("eventAddWire");
   
   /**
    * Event that is fired when a wire is removed
    * You can register this event with myTerminal.eventRemoveWire.subscribe(function(e,params) { var wire=params[0];}, scope);
    * @event eventRemoveWire
    */
   this.eventRemoveWire = new YAHOO.util.CustomEvent("eventRemoveWire");
   
   /**
    * Event that is fired when a container is added
    * You can register this event with myTerminal.eventAddContainer.subscribe(function(e,params) { var container=params[0];}, scope);
    * @event eventAddContainer
    */
   this.eventAddContainer = new YAHOO.util.CustomEvent("eventAddContainer");
   
   /**
    * Event that is fired when a container is removed
    * You can register this event with myTerminal.eventRemoveContainer.subscribe(function(e,params) { var container=params[0];}, scope);
    * @event eventRemoveContainer
    */
   this.eventRemoveContainer = new YAHOO.util.CustomEvent("eventRemoveContainer");
   
   /**
    * Event that is fired when a container has been moved
    * You can register this event with myTerminal.eventContainerDragged.subscribe(function(e,params) { var container=params[0];}, scope);
    * @event eventContainerDragged
    */
   this.eventContainerDragged = new YAHOO.util.CustomEvent("eventContainerDragged");
   
   /**
    * Event that is fired when a container has been resized
    * You can register this event with myTerminal.eventContainerResized.subscribe(function(e,params) { var container=params[0];}, scope);
    * @event eventContainerResized
    */
   this.eventContainerResized = new YAHOO.util.CustomEvent("eventContainerResized");
   
   this.render();
   
	if( options.containers ) {
		this.initContainers(options.containers);
	}
   
	if( options.wires ) {
   	this.initWires(options.wires);
	}
   
   if(this.layerMap) { 
		this.layermap = new WireIt.LayerMap(this, this.layerMapOptions);
   }
   
	if(WireIt.Grouper) {
	   this.grouper = new WireIt.Grouper(this, this.grouper.baseConfigFunction);
   
	   var rb = this.grouper.rubberband;
		this.el.onmousedown = function(event) { return rb.layerMouseDown.call(rb, event); };
	   var grouper = this.grouper;
	   this.el.addEventListener("mouseup", function (event)  { 
		    rb.finish(); 
		    grouper.rubberbandSelect.call(grouper); 
		}, false);
	}
};

WireIt.Layer.prototype = {

	/** 
    * @property className
    * @description CSS class name for the layer element
    * @default "WireIt-Layer"
    * @type String
    */
	className: "WireIt-Layer",
	
	/** 
    * @property parentEl
    * @description DOM element that schould contain the layer
    * @default null
    * @type DOMElement
    */
	parentEl: null,

	/** 
    * @property layerMap
    * @description Display the layer map
    * @default false
    * @type Boolean
    */
	layerMap: false,

	/** 
    * @property layerMapOptions
    * @description Options for the layer map
    * @default null
    * @type Object
    */
	layerMapOptions: null,

	/** 
    * @property enableMouseEvents
    * @description Enable the mouse events
    * @default true
    * @type Boolean
    */
	enableMouseEvents: true,

	/**
	 * TODO
	 */
	grouper: null, 

	/**
    * Set the options by putting them in this (so it overrides the prototype default)
    * @method setOptions
    */
   setOptions: function(options) {
      for(var k in options) {
			if( options.hasOwnProperty(k) ) {
				this[k] = options[k];
			}
		}
		
		if(!this.parentEl) {
			this.parentEl = document.body;
		}
		
   },

   /**
    * Create the dom of the layer and insert it into the parent element
    * @method render
    */
   render: function() {
      this.el = WireIt.cn('div', {className: this.className} );   
      this.parentEl.appendChild(this.el);
   },


   /**
    * Create all the containers passed as options
    * @method initContainers
    */
   initContainers: function(containers) {
      for(var i = 0 ; i < containers.length ; i++) {
         this.addContainer(containers[i]);
      } 
   },

   /**
    * Create all the wires passed in the config
    * @method initWires
    */
   initWires: function(wires) {
      for(var i = 0 ; i < wires.length ; i++) {
         this.addWire(wires[i]);
      }
   },

	/**
	 * TODO
	 */
	setSuperHighlighted: function(containers) {
		this.unsetSuperHighlighted();
		for (var i in containers) {
			if(containers.hasOwnProperty(i)) {
				containers[i].superHighlight();
			}
		}
		this.superHighlighted = containers;
	},

	/**
	 * TODO
	 */
	unsetSuperHighlighted: function() {
		if (YAHOO.lang.isValue(this.superHighlighted)) {
			for (var i in this.superHighlighted) {
				if(this.superHighlighted.hasOwnProperty(i)) {
					this.superHighlighted[i].highlight();
				}
			}
		}
		this.superHighlighted = null;
	},

   /**
    * Instanciate a wire given its "xtype" (default to WireIt.Wire)
    * @method addWire
    * @param {Object} wireConfig  Wire configuration object (see WireIt.Wire class for details)
    * @return {WireIt.Wire} Wire instance build from the xtype
    */
   addWire: function(wireConfig) {
	
		var klass = WireIt.wireClassFromXtype(wireConfig.xtype);
   
      var src = wireConfig.src;
      var tgt = wireConfig.tgt;
   
      var terminal1 = this.containers[src.moduleId].getTerminal(src.terminal);
      var terminal2 = this.containers[tgt.moduleId].getTerminal(tgt.terminal);
      var wire = new klass( terminal1, terminal2, this.el, wireConfig);
      wire.redraw();
   
      return wire;
   },

   /**
    * Instanciate a container given its "xtype": WireIt.Container (default) or a subclass of it.
    * @method addContainer
    * @param {Object} containerConfig  Container configuration object (see WireIt.Container class for details)
    * @return {WireIt.Container} Container instance build from the xtype
    */
   addContainer: function(containerConfig) {

		var klass = WireIt.containerClassFromXtype(containerConfig.xtype);

      var container = new klass(containerConfig, this);
   
      return this.addContainerDirect(container);
   },


   addContainerDirect: function(container) {
      this.containers.push( container );
   
      // Event listeners
      container.eventAddWire.subscribe(this.onAddWire, this, true);
      container.eventRemoveWire.subscribe(this.onRemoveWire, this, true);
   
      if(container.ddResize) {
         container.ddResize.on('endDragEvent', function() {
            this.eventContainerResized.fire(container);
				this.eventChanged.fire(this);
         }, this, true);
      }
      if(container.dd) {
         container.dd.on('endDragEvent', function() {
            this.eventContainerDragged.fire(container);
				this.eventChanged.fire(this);
         }, this, true);
      }
   
      this.eventAddContainer.fire(container);

		this.eventChanged.fire(this);
   
      return container;	
   },
   
   /**
    * Remove a container
    * @method removeContainer
    * @param {WireIt.Container} container Container instance to remove
    */
   removeContainer: function(container) {
      var index = WireIt.indexOf(container, this.containers);
      if( index != -1 ) {
	  
	container.remove();
	    
        this.containers[index] = null;
        this.containers = WireIt.compact(this.containers);
      
	this.eventRemoveContainer.fire(container);

	this.eventChanged.fire(this);
      }
   },

	/**
	 * TODO
	 */
	removeGroup: function(group, containersAsWell)  {
		var index = this.groups.indexOf(group) , i;
		
		if (index != -1) {
			this.groups.splice(index, 1);
		}

		if (containersAsWell) {
			if (YAHOO.lang.isValue(group.groupContainer)) {
				this.removeContainer(group.groupContainer);
			}
			else {
				for (i in group.containers) {
					if(group.containers.hasOwnProperty(i)) {
						var elem = group.containers[i].container;
						this.removeContainer(elem);
					}
				}

				for (i in group.groups) {
					if(group.containers.hasOwnProperty(i)) {
						var g = group.groups[i].group;
						this.removeGroup(g);
					}
				}
			}
		}
	},

   /**
    * Update the wire list when any of the containers fired the eventAddWire
    * @method onAddWire
    * @param {Event} event The eventAddWire event fired by the container
    * @param {Array} args This array contains a single element args[0] which is the added Wire instance
    */
   onAddWire: function(event, args) {
      var wire = args[0];
      // add the wire to the list if it isn't in
      if( WireIt.indexOf(wire, this.wires) == -1 ) {
         this.wires.push(wire);
         
         if(this.enableMouseEvents) {
            YAHOO.util.Event.addListener(wire.element, "mousemove", this.onWireMouseMove, this, true);
            YAHOO.util.Event.addListener(wire.element, "click", this.onWireClick, this, true);
         }
         
         // Re-Fire an event at the layer level
         this.eventAddWire.fire(wire);

			// Fire the layer changed event
			this.eventChanged.fire(this);
      }
   },

   /**
    * Update the wire list when a wire is removed
    * @method onRemoveWire
    * @param {Event} event The eventRemoveWire event fired by the container
    * @param {Array} args This array contains a single element args[0] which is the removed Wire instance
    */
   onRemoveWire: function(event, args) {
      var wire = args[0];
      var index = WireIt.indexOf(wire, this.wires);
      if( index != -1 ) {
         this.wires[index] = null;
         this.wires = WireIt.compact(this.wires);
         this.eventRemoveWire.fire(wire);
			this.eventChanged.fire(this);
      }
   },


   /**
    * Remove all the containers in this layer (and the associated terminals and wires)
    * @method clear
    */
   clear: function() {
		while(this.containers.length > 0) {
         this.removeContainer(this.containers[0]);
      }
   },

   /**
    * @deprecated Alias for clear
    * @method removeAllContainers
    */
   removeAllContainers: function() {
      this.clear();
   },


   /**
    * Return an object that represent the state of the layer including the containers and the wires
    * @method getWiring
    * @return {Obj} layer configuration
    */
   getWiring: function() {
   
      var i;
      var obj = {containers: [], wires: []};
   
      for( i = 0 ; i < this.containers.length ; i++) {
         obj.containers.push( this.containers[i].getConfig() );
      }
   
      for( i = 0 ; i < this.wires.length ; i++) {
         var wire = this.wires[i];
      	var wireObj = wire.getConfig();
			wireObj.src = {moduleId: WireIt.indexOf(wire.terminal1.container, this.containers), terminal: wire.terminal1.name };
			wireObj.tgt = {moduleId: WireIt.indexOf(wire.terminal2.container, this.containers), terminal: wire.terminal2.name };
         obj.wires.push(wireObj);
      }
   
      return obj;
   },

   /**
    * Load a layer configuration object
    * @method setWiring
    * @param {Object} wiring layer configuration
    */
   setWiring: function(wiring) {
      this.clear();
      var i;
      if(YAHOO.lang.isArray(wiring.containers)) {
         for(i = 0 ; i < wiring.containers.length ; i++) {
            this.addContainer(wiring.containers[i]);
         }
      }
      if(YAHOO.lang.isArray(wiring.wires)) {
         for(i = 0 ; i < wiring.wires.length ; i++) {
            this.addWire(wiring.wires[i]);
         }
       }
   },
   
   /**
    * Returns a position relative to the layer from a mouse event
    * @method _getMouseEvtPos
    * @param {Event} e Mouse event
    * @return {Array} position
    */
   _getMouseEvtPos: function(e) {
		var tgt = YAHOO.util.Event.getTarget(e);
		var tgtPos = [tgt.offsetLeft, tgt.offsetTop];
		return [tgtPos[0]+e.layerX, tgtPos[1]+e.layerY];
   },

   /**
    * Handles click on any wire canvas
    * Note: we treat mouse events globally so that wires behind others can still receive the events
    * @method onWireClick
    * @param {Event} e Mouse click event
    */
   onWireClick: function(e) {
      var p = this._getMouseEvtPos(e);
		var lx = p[0], ly = p[1], n = this.wires.length, w;
		for(var i = 0 ; i < n ; i++) {
			w = this.wires[i];
			var elx = w.element.offsetLeft, ely = w.element.offsetTop;
			// Check if the mouse is within the canvas boundaries
			if( lx >= elx && lx < elx+w.element.width && ly >= ely && ly < ely+w.element.height ) {
				var rx = lx-elx, ry = ly-ely; // relative to the canvas
				w.onClick(rx,ry);
			}
		}
	},

   /**
    * Handles mousemove events on any wire canvas
    * Note: we treat mouse events globally so that wires behind others can still receive the events
    * @method onWireMouseMove
    * @param {Event} e Mouse click event
    */
   onWireMouseMove: function(e) {
      var p = this._getMouseEvtPos(e);
		var lx = p[0], ly = p[1], n = this.wires.length, w;
		for(var i = 0 ; i < n ; i++) {
			w = this.wires[i];
			var elx = w.element.offsetLeft, ely = w.element.offsetTop;
			// Check if the mouse is within the canvas boundaries
			if( lx >= elx && lx < elx+w.element.width && ly >= ely && ly < ely+w.element.height ) {
				var rx = lx-elx, ry = ly-ely; // relative to the canvas
				w.onMouseMove(rx,ry);
			}
		}
	}

};
