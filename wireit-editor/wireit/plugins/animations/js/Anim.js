/**
 * Some utility classes to provide animations in WireIt
 * @module animations-plugin
 */

/**
 * WireIt.util.Anim is a wrapper class for YAHOO.util.Anim, to redraw the wires associated with the given terminals while running the animation.
 * @class Anim
 * @namespace WireIt.util
 * @extends YAHOO.util.Anim
 * @constructor
 * @param {Array} terminals List of WireIt.Terminal objects associated within the animated element
 * @params {String} id Parameter of YAHOO.util.Anim
 * @params {String} sGroup Parameter of YAHOO.util.Anim
 * @params {Object} config Parameter of YAHOO.util.Anim
 */
WireIt.util.Anim = function( terminals, el, attributes, duration, method) {
   if(!terminals) {
      throw new Error("WireIt.util.Anim needs at least terminals and id");
   }
   
   /**
    * List of the contained terminals
    * @property _WireItTerminals
    * @type {Array}
    */
   this._WireItTerminals = terminals;
   
   WireIt.util.Anim.superclass.constructor.call(this, el, attributes, duration, method);
   
   // Subscribe the onTween event to move the wires
   this.onTween.subscribe(this.moveWireItWires, this, true);
};

YAHOO.extend(WireIt.util.Anim, YAHOO.util.Anim, {
   
   /**
    * Listen YAHOO.util.Anim.onTween events to redraw the wires
    * @method moveWireItWires
    */
   moveWireItWires: function(e) {
      // Make sure terminalList is an array
      var terminalList = YAHOO.lang.isArray(this._WireItTerminals) ? this._WireItTerminals : (this._WireItTerminals.isWireItTerminal ? [this._WireItTerminals] : []);
      // Redraw all the wires
      for(var i = 0 ; i < terminalList.length ; i++) {
         if(terminalList[i].wires) {
            for(var k = 0 ; k < terminalList[i].wires.length ; k++) {
               terminalList[i].wires[k].redraw();
            }
         }
      }
   },

   /**
    * In case you change the terminals since you created the WireIt.util.Anim:
    * @method setTerminals
    * @param {Array} terminals
    */
   setTerminals: function(terminals) {
      this._WireItTerminals = terminals;
   }

});