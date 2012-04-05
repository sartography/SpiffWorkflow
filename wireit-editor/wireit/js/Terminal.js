/*global YAHOO */
(function() {

   var util = YAHOO.util;
   var Event = util.Event, lang = YAHOO.lang, Dom = util.Dom, CSS_PREFIX = "WireIt-";

/**
 * Terminals represent the end points of the "wires"
 * @class Terminal
 * @constructor
 * @param {HTMLElement} parentEl Element that will contain the terminal
 * @param {Object} options Configuration object
 * @param {WireIt.Container} container (Optional) Container containing this terminal
 */
WireIt.Terminal = function(parentEl, options, container) {

	/**
    * @property name
	 * @description Name of the terminal
    * @type String
    * @default null
    */
	this.name = null;

   /**
    * @property parentEl
	 * @description DOM parent element
    * @type DOMElement
    */
   this.parentEl = parentEl;
   
   /**
    * @property container
	 * @description Container (optional). Parent container of this terminal
    * @type WireIt.Container
    */
   this.container = container;
   
   /**
    * @property wires
	 * @description List of the associated wires
    * @type Array
    */
    this.wires = [];
   
   
   this.setOptions(options);
   
   /**
    * Event that is fired when a wire is added
    * You can register this event with myTerminal.eventAddWire.subscribe(function(e,params) { var wire=params[0];}, scope);
    * @event eventAddWire
    */
   this.eventAddWire = new util.CustomEvent("eventAddWire");
   
   /**
    * Event that is fired when a wire is removed
    * You can register this event with myTerminal.eventRemoveWire.subscribe(function(e,params) { var wire=params[0];}, scope);
    * @event eventRemoveWire
    */
   this.eventRemoveWire = new util.CustomEvent("eventRemoveWire");
   
   /**
    * DIV dom element that will display the Terminal
    * @property el
    * @type {HTMLElement}
    */
   this.el = null;
   
   
   this.render();
   
   // Create the TerminalProxy object to make the terminal editable
   if(this.editable) {
      this.dd = new WireIt.TerminalProxy(this, this.ddConfig);
      this.scissors = new WireIt.Scissors(this);
   }
};

WireIt.Terminal.prototype = {

	/** 
    * @property xtype
    * @description String representing this class for exporting as JSON
    * @default "WireIt.Terminal"
    * @type String
    */
   xtype: "WireIt.Terminal",

	/**
    * @property direction
	 * @description direction vector of the wires when connected to this terminal
    * @type Array
    * @default [0,1]
    */
	direction: [0,1],
	
	/**
    * @property fakeDirection
	 * @description direction vector of the "editing" wire when it started from this terminal
    * @type Array
    * @default [0,-1]
    */
	fakeDirection: [0,-1],

	/**
    * @property editable
	 * @description boolean that makes the terminal editable
    * @type Boolean
    * @default true
    */
	editable: true,
	
	/**
    * @property nMaxWires
	 * @description maximum number of wires for this terminal
    * @type Integer
    * @default Infinity
    */
	nMaxWires: Infinity,

	/**
    * @property wireConfig
	 * @description Options for the wires connected to this terminal
    * @type Object
    * @default {}
    */
	wireConfig: {},
	
	/**
    * @property editingWireConfig
	 * @description Options for the wires connected to this terminal
    * @type Object
    * @default {}
    */
	editingWireConfig: {},
	
	/** 
    * @property className
    * @description CSS class name for the terminal element
    * @default "WireIt-Terminal"
    * @type String
    */
	className: "WireIt-Terminal",
	
	/** 
    * @property connectedClassName
    * @description CSS class added to the terminal when it is connected
    * @default "WireIt-connected"
    * @type String
    */
	connectedClassName: "WireIt-Terminal-connected",
	
	/** 
    * @property dropinviteClassName
    * @description CSS class added for drop invitation
    * @default "WireIt-dropinvite"
    * @type String
    */
	dropinviteClassName: "WireIt-Terminal-dropinvite",

	/** 
    * @property offsetPosition
    * @description offset position from the parentEl position. Can be an array [top,left] or an object {left: 100, bottom: 20} or {right: 10, top: 5} etc...
    * @default null
    * @type Array
    */
	offsetPosition: null,
	
	/**
    * @property alwaysSrc
	 * @description forces this terminal to be the src terminal in the wire config
    * @type Boolean
    * @default false
    */
	alwaysSrc: false,
	
	/**
    * @property ddConfig
	 * @description configuration of the WireIt.TerminalProxy object
    * @type Object
    * @default {}
    */
	ddConfig: false,


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
		
		// Set fakeDirection to the opposite of direction
		if(options.direction && !options.fakeDirection) {
			this.fakeDirection = [ -options.direction[0], -options.direction[1] ];
		}
		
		// Set the editingWireConfig to the wireConfig if specified
		if(options.wireConfig && !options.editingWireConfig) {
			this.editingWireConfig = this.wireConfig;
		}
   },

   /**
    * Show or hide the drop invitation. (by adding/removing this.options.dropinviteClassName CSS class)
    * @method setDropInvitation
    * @param {Boolean} display Show the invitation if true, hide it otherwise
    */
   setDropInvitation: function(display) {
      if(display) {
         Dom.addClass(this.el, this.dropinviteClassName);
      }
      else {
         Dom.removeClass(this.el, this.dropinviteClassName);
      }
   },

   /**
    * Render the DOM of the terminal
    * @method render
    */
   render: function() {
   
      // Create the DIV element
      this.el = WireIt.cn('div', {className: this.className} );
      if(this.name) { this.el.title = this.name; }

      // Set the offset position
      this.setPosition(this.offsetPosition);
   
      // Append the element to the parent
      this.parentEl.appendChild(this.el);
   },

	/**
	 * TODO
	 */
   setPosition: function(pos) {
		if(pos) {
			// Clear the current position
			this.el.style.left = "";
			this.el.style.top = "";
			this.el.style.right = "";
			this.el.style.bottom = "";
	    
			// Kept old version [x,y] for retro-compatibility
			if( lang.isArray(pos) ) {
				this.el.style.left = pos[0]+"px";
				this.el.style.top = pos[1]+"px";
			}
			// New version: {top: 32, left: 23}
			else if( lang.isObject(pos) ) {
				for(var key in pos) {
					if(pos.hasOwnProperty(key) && pos[key] !== ""){ //This will ignore the number 0 since 0 == "" in javascript (firefox 3.0
						this.el.style[key] = pos[key]+"px";
					}
				}
			}
		}
	},
    
   /**
    * Add a wire to this terminal.
    * @method addWire
    * @param {WireIt.Wire} wire Wire instance to add
    */
   addWire: function(wire) {
   
      // Adds this wire to the list of connected wires :
      this.wires.push(wire);
   
      // Set class indicating that the wire is connected
      Dom.addClass(this.el, this.connectedClassName);
   
      // Fire the event
      this.eventAddWire.fire(wire);
   },

   /**
    * Remove a wire
    * @method removeWire
    * @param {WireIt.Wire} wire Wire instance to remove
    */
   removeWire: function(wire) {
      var index = WireIt.indexOf(wire, this.wires); 
      if( index != -1 ) {
         
         this.wires[index].destroy();
         
         this.wires[index] = null;
         this.wires = WireIt.compact(this.wires);
      
         // Remove the connected class if it has no more wires:
         if(this.wires.length === 0) {
            Dom.removeClass(this.el, this.connectedClassName);
         }
      
         // Fire the event
         this.eventRemoveWire.fire(wire);
      }
   },

   /**
    * This function is a temporary test. I added the border width while traversing the DOM and
    * I calculated the offset to center the wire in the terminal just after its creation
    * @method getXY
    */
   getXY: function() {
   
      var layerEl = this.container && this.container.layer ? this.container.layer.el : document.body;

      var obj = this.el;
		var curleft = 0, curtop = 0;
		if (obj.offsetParent) {
			do {
				curleft += obj.offsetLeft;
				curtop += obj.offsetTop;
				obj = obj.offsetParent;
			} while ( !!obj && obj != layerEl);
		}

		return [curleft+15,curtop+15];
   },

   /**
    * Remove the terminal from the DOM
    * @method remove
    */
   remove: function() {
      // This isn't very nice but...
      // the method Wire.remove calls Terminal.removeWire to remove the reference
      while(this.wires.length > 0) {
         this.wires[0].remove();
      }
      this.parentEl.removeChild(this.el);
      
      // Remove all event listeners
      Event.purgeElement(this.el);
      
      // Remove scissors widget
      if(this.scissors) {
         Event.purgeElement(this.scissors.get('element'));
      }
      
   },

   /**
    * Returns a list of all the terminals connecter to this terminal through its wires.
    * @method getConnectedTerminals
    * @return  {Array}  List of all connected terminals
    */
   getConnectedTerminals: function() {
      var terminalList = [];
      if(this.wires) {
         for(var i = 0 ; i < this.wires.length ; i++) {
            terminalList.push(this.wires[i].getOtherTerminal(this));
         }
      }
      return terminalList;
   },

   /**
    * Redraw all the wires connected to this terminal
    * @method redrawAllWires
    */
   redrawAllWires: function() {
      if(this.wires) {
         for(var i = 0 ; i < this.wires.length ; i++) {
            this.wires[i].redraw();
         }
      }
   },
   
   /** 
    * Remove all wires
    * @method removeAllWires
    */
   removeAllWires: function() {
      while(this.wires.length > 0) {
         this.wires[0].remove();
      }
   }

};

})();