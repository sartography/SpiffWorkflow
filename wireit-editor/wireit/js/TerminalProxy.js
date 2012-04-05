/*global YAHOO,window */
(function() {

   var util = YAHOO.util;
   var lang = YAHOO.lang, CSS_PREFIX = "WireIt-";

/**
 * This class is used for wire edition. It inherits from YAHOO.util.DDProxy and acts as a "temporary" Terminal.
 * @class TerminalProxy
 * @namespace WireIt
 * @extends YAHOO.util.DDProxy
 * @constructor
 * @param {WireIt.Terminal} terminal Parent terminal
 * @param {Object} options Configuration object (see "termConfig" property for details)
 */
WireIt.TerminalProxy = function(terminal, options) {

	/**
	 * Reference to the terminal parent
	 */
	this.terminal = terminal;

	/**
	 * Object containing the configuration object
	 * <ul>
	 *   <li>type: 'type' of this terminal. If no "allowedTypes" is specified in the options, the terminal will only connect to the same type of terminal</li>
	 *   <li>allowedTypes: list of all the allowed types that we can connect to.</li>
	 *   <li>{Integer} terminalProxySize: size of the drag drop proxy element. default is 10 for "10px"</li>
	 * </ul>
	 * @property termConfig
	 */
	// WARNING: the object config cannot be called "config" because YAHOO.util.DDProxy already has a "config" property
	this.termConfig = options || {};

	this.terminalProxySize = options.terminalProxySize || 10;

	/**
	 * Object that emulate a terminal which is following the mouse
	 */
	this.fakeTerminal = null;

	// Init the DDProxy
	WireIt.TerminalProxy.superclass.constructor.call(this,this.terminal.el, undefined, {
	   dragElId: "WireIt-TerminalProxy",
	   resizeFrame: false,
	   centerFrame: true
	});
	
};

// Mode Intersect to get the DD objects
util.DDM.mode = util.DDM.INTERSECT;

lang.extend(WireIt.TerminalProxy, YAHOO.util.DDProxy, {

	/**
	 * Took this method from the YAHOO.util.DDProxy class
	 * to overwrite the creation of the proxy Element with our custom size
	 * @method createFrame
	 */
	createFrame: function() {
	 	var self=this, body=document.body;
     	if (!body || !body.firstChild) {
       	window.setTimeout( function() { self.createFrame(); }, 50 );
         return;
     	}
     	var div=this.getDragEl(), Dom=YAHOO.util.Dom;
     	if (!div) {
         div    = document.createElement("div");
         div.id = this.dragElId;
         var s  = div.style;
         s.position   = "absolute";
         s.visibility = "hidden";
         s.cursor     = "move";
         s.border     = "2px solid #aaa";
         s.zIndex     = 999;
         var size = this.terminalProxySize+"px";
         s.height     = size; 
         s.width      = size;
         var _data = document.createElement('div');
         Dom.setStyle(_data, 'height', '100%');
         Dom.setStyle(_data, 'width', '100%');
         Dom.setStyle(_data, 'background-color', '#ccc');
         Dom.setStyle(_data, 'opacity', '0');
         div.appendChild(_data);
         body.insertBefore(div, body.firstChild);
     	}
 	},

	/**
	 * @method startDrag
	 */
	startDrag: function() {
   
	   // If only one wire admitted, we remove the previous wire
	   if(this.terminal.nMaxWires == 1 && this.terminal.wires.length == 1) {
	      this.terminal.wires[0].remove();
	   }
	   // If the number of wires is at its maximum, prevent editing...
	   else if(this.terminal.wires.length >= this.terminal.nMaxWires) {
	      return;
	   }
   
	   var halfProxySize = this.terminalProxySize/2;
	   this.fakeTerminal = {
	      direction: this.terminal.fakeDirection,
	      pos: [200,200], 
	      addWire: function() {},
	      removeWire: function() {},
	      getXY: function() { 
	         var layers = YAHOO.util.Dom.getElementsByClassName('WireIt-Layer');
	         if(layers.length > 0) {
	            var orig = YAHOO.util.Dom.getXY(layers[0]);
	            return [this.pos[0]-orig[0]+halfProxySize, this.pos[1]-orig[1]+halfProxySize]; 
	         }
	         return this.pos;
	      }
	   };
   
	   var parentEl = this.terminal.parentEl.parentNode;
	   if(this.terminal.container) {
	      parentEl = this.terminal.container.layer.el;
	   }
	
		var klass = WireIt.wireClassFromXtype(this.terminal.editingWireConfig.xtype);
		
	   this.editingWire = new klass(this.terminal, this.fakeTerminal, parentEl, this.terminal.editingWireConfig);
	   YAHOO.util.Dom.addClass(this.editingWire.element, CSS_PREFIX+'Wire-editing');
	},

	/**
	 * @method onDrag
	 */
	onDrag: function(e) {
   
	   // Prevention when the editing wire could not be created (due to nMaxWires)
	   if(!this.editingWire) { return; }
   
	   if(this.terminal.container) {
			var obj = this.terminal.container.layer.el;
         var curleft = 0;
         // Applied patch from http://github.com/neyric/wireit/issues/#issue/27
         // Fixes issue with Wire arrow being drawn offset to the mouse pointer
         var curtop = 0;
         if (obj.offsetParent) {
           do {
             curleft += obj.scrollLeft;
             curtop += obj.scrollTop;
             obj = obj.offsetParent ;
           } while ( obj );
         }
         this.fakeTerminal.pos = [e.clientX+curleft, e.clientY+curtop];
	   }
	   else {
	      this.fakeTerminal.pos = (YAHOO.env.ua.ie) ? [e.clientX, e.clientY] : [e.clientX+window.pageXOffset, e.clientY+window.pageYOffset];
	   }
	   this.editingWire.redraw();
	},


	/**
	 * @method endDrag
	 */
	endDrag: function(e) {
	   if(this.editingWire) {
	      this.editingWire.remove();
	      this.editingWire = null;
	   }
	},

	/**
	 * @method onDragEnter
	 */
	onDragEnter: function(e,ddTargets) {
   
	   // Prevention when the editing wire could not be created (due to nMaxWires)
	   if(!this.editingWire) { return; }
   
	   for(var i = 0 ; i < ddTargets.length ; i++) {
	      if( this.isValidWireTerminal(ddTargets[i]) ) {
	         ddTargets[i].terminal.setDropInvitation(true);
	      }
	   }
	},

	/**
	 * @method onDragOut
	 */
	onDragOut: function(e,ddTargets) { 
   
	   // Prevention when the editing wire could not be created (due to nMaxWires)
	   if(!this.editingWire) { return; }
   
	   for(var i = 0 ; i < ddTargets.length ; i++) {
	      if( this.isValidWireTerminal(ddTargets[i]) ) {
	         ddTargets[i].terminal.setDropInvitation(false);
	      }
	   }
	},

	/**
	 * @method onDragDrop
	 */
	onDragDrop: function(e,ddTargets) {

		var i;

	   // Prevention when the editing wire could not be created (due to nMaxWires)
	   if(!this.editingWire) { return; }
   
	   this.onDragOut(e,ddTargets);
   
	   // Connect to the FIRST target terminal
	   var targetTerminalProxy = null;
	   for(i = 0 ; i < ddTargets.length ; i++) {
	      if( this.isValidWireTerminal(ddTargets[i]) ) {
	         targetTerminalProxy =  ddTargets[i];
	         break;
	      }
	   }

	   // Quit if no valid terminal found
	   if( !targetTerminalProxy ) { 
	      return;
	   }
   
	   // Remove the editing wire
	   this.editingWire.remove();
	   this.editingWire = null;
      
	   // Don't create the wire if it already exists between the 2 terminals !!
	   var termAlreadyConnected = false;
	   for(i = 0 ; i < this.terminal.wires.length ; i++) {
	      if(this.terminal.wires[i].terminal1 == this.terminal) {
	         if( this.terminal.wires[i].terminal2 == targetTerminalProxy.terminal) {
	            termAlreadyConnected = true;
	            break;
	         }
	      }
	      else if(this.terminal.wires[i].terminal2 == this.terminal) {
	         if( this.terminal.wires[i].terminal1 == targetTerminalProxy.terminal) {
	            termAlreadyConnected = true;
	            break;
	         }
	      }
	   }
   
	   // Create the wire only if the terminals aren't connected yet
	   if(termAlreadyConnected) {
	      //console.log("terminals already connected ");
	      return;
	   }
      
	   var parentEl = this.terminal.parentEl.parentNode;
	   if(this.terminal.container) {
	      parentEl = this.terminal.container.layer.el;
	   }
   
	   // Switch the order of the terminals if tgt as the "alwaysSrc" property
	   var term1 = this.terminal;
	   var term2 = targetTerminalProxy.terminal;
	   if(term2.alwaysSrc) {
	      term1 = targetTerminalProxy.terminal;
	      term2 = this.terminal;
	   }
	
		var klass = WireIt.wireClassFromXtype(term1.wireConfig.xtype);
   
	   // Check the number of wires for this terminal
	   var tgtTerm = targetTerminalProxy.terminal, w;
	   if( tgtTerm.nMaxWires == 1) {
	      if(tgtTerm.wires.length > 0) {
	         tgtTerm.wires[0].remove();
	      }
	
	      w = new klass(term1, term2, parentEl, term1.wireConfig);
	      w.redraw();
	   }
	   else if(tgtTerm.wires.length < tgtTerm.nMaxWires) {
	      w = new klass(term1, term2, parentEl, term1.wireConfig);
	      w.redraw();
	   }
	   /*else {
	      console.log("Cannot connect to this terminal: nMaxWires = ", ddTargets[0].terminal.nMaxWires);
	   }*/
   
	},


	// to distinct from other YAHOO.util.DragDrop objects
	isWireItTerminal: true,


	/**
	 * @method isValidWireTerminal
	 */
	isValidWireTerminal: function(DDterminal) {
   
	   if( !DDterminal.isWireItTerminal ) {
	      return false;
	   }
   
	   // If this terminal has the type property:
	   if(this.termConfig.type) {
	      if(this.termConfig.allowedTypes) {
	         if( WireIt.indexOf(DDterminal.termConfig.type, this.termConfig.allowedTypes) == -1 ) {
	            return false;
	         }
	      }
	      else {
	         if(this.termConfig.type != DDterminal.termConfig.type) {
	            return false;
	         }
	      }
	   }
	   // The other terminal may have type property too:
	   else if(DDterminal.termConfig.type) {
	      if(DDterminal.termConfig.allowedTypes) {
	         if( WireIt.indexOf(this.termConfig.type, DDterminal.termConfig.allowedTypes) == -1 ) {
	            return false;
	         }
	      }
	      else {
	         if(this.termConfig.type != DDterminal.termConfig.type) {
	            return false;
	         }
	      }
	   }
   
	   // Check the allowSelfWiring
	   if(this.terminal.container) {
	      if(this.terminal.container.preventSelfWiring) {
	         if(DDterminal.terminal.container == this.terminal.container) {
	            return false;
	         }
	      }
	   }
   
	   return true;
	}

});

})();