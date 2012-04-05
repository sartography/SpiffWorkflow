/*global YAHOO */
(function() {

   var util = YAHOO.util;
	var Event = util.Event, lang = YAHOO.lang, CSS_PREFIX = "WireIt-";

/**
 * Scissors widget to cut wires
 * @class Scissors
 * @namespace WireIt
 * @extends YAHOO.util.Element
 * @constructor
 * @param {WireIt.Terminal} terminal Associated terminal
 * @param {Object} oConfigs 
 */
WireIt.Scissors = function(terminal, oConfigs) {
   WireIt.Scissors.superclass.constructor.call(this, document.createElement('div'), oConfigs);

   /**
    * The terminal it is associated to
    * @property _terminal
    * @type {WireIt.Terminal}
    */
   this._terminal = terminal;
   
   this.initScissors();
};

WireIt.Scissors.visibleInstance = null;

lang.extend(WireIt.Scissors, YAHOO.util.Element, {
   
   /**
    * Init the scissors
    * @method initScissors
    */
   initScissors: function() {
      
      // Display the cut button
      this.hideNow();
      this.addClass(CSS_PREFIX+"Wire-scissors");
      
      // The scissors are within the terminal element
      this.appendTo(this._terminal.container ? this._terminal.container.layer.el : this._terminal.el.parentNode.parentNode);

      // Ajoute un listener sur le scissor:
      this.on("mouseover", this.show, this, true);
      this.on("mouseout", this.hide, this, true);
      this.on("click", this.scissorClick, this, true);
      
      // On mouseover/mouseout to display/hide the scissors
      Event.addListener(this._terminal.el, "mouseover", this.mouseOver, this, true);
      Event.addListener(this._terminal.el, "mouseout", this.hide, this, true);
   },
   
   /**
    * @method setPosition
    */
   setPosition: function() {
      var pos = this._terminal.getXY();
      this.setStyle("left", (pos[0]+this._terminal.direction[0]*30-8)+"px");
      this.setStyle("top", (pos[1]+this._terminal.direction[1]*30-8)+"px");
   },
   /**
    * @method mouseOver
    */
   mouseOver: function() {
      if(this._terminal.wires.length > 0)  {
         this.show();
      }
   },

   /**
    * @method scissorClick
    */
   scissorClick: function() {
      this._terminal.removeAllWires();
      if(this.terminalTimeout) { this.terminalTimeout.cancel(); }
      this.hideNow();
   },   
   /**
    * @method show
    */
   show: function() {
      this.setPosition();
      this.setStyle('display','');
		
		if(WireIt.Scissors.visibleInstance && WireIt.Scissors.visibleInstance != this) {
			if(WireIt.Scissors.visibleInstance.terminalTimeout) { WireIt.Scissors.visibleInstance.terminalTimeout.cancel(); }
			WireIt.Scissors.visibleInstance.hideNow(); 
		}
		WireIt.Scissors.visibleInstance = this;
		
      if(this.terminalTimeout) { this.terminalTimeout.cancel(); }
   },
   /**
    * @method hide
    */
   hide: function() {
      this.terminalTimeout = YAHOO.lang.later(700,this,this.hideNow);
   },
   /**
    * @method hideNow
    */
   hideNow: function() {
		WireIt.Scissors.visibleInstance = null;
      this.setStyle('display','none');
   }

});

})();