/*global YAHOO */
/**
 * Class that extends Terminal to differenciate Input/Output terminals
 * @class WireIt.util.TerminalInput
 * @extends WireIt.Terminal
 * @constructor
 * @param {HTMLElement} parentEl Parent dom element
 * @param {Object} options configuration object
 * @param {WireIt.Container} container (Optional) Container containing this terminal
 */
WireIt.util.TerminalInput = function(parentEl, options, container) {
   WireIt.util.TerminalInput.superclass.constructor.call(this,parentEl, options, container);
};
YAHOO.lang.extend(WireIt.util.TerminalInput, WireIt.Terminal, {

	/** 
    * @property xtype
    * @description String representing this class for exporting as JSON
    * @default "WireIt.TerminalInput"
    * @type String
    */
   xtype: "WireIt.TerminalInput",

	/**
    * @property direction
	 * @description direction vector of the wires when connected to this terminal
    * @type Array
    * @default [0,-1]
    */
	direction: [0,-1],
	
	/**
    * @property fakeDirection
	 * @description direction vector of the "editing" wire when it started from this terminal
    * @type Array
    * @default [0,1]
    */
	fakeDirection: [0,1],
   
	/**
    * @property nMaxWires
	 * @description maximum number of wires for this terminal
    * @type Integer
    * @default 1
    */
	nMaxWires: 1,
	
	/**
    * @property ddConfig
	 * @description configuration of the WireIt.TerminalProxy object
    * @type Object
    * @default { type: "input", allowedTypes: ["output"] }
    */
	ddConfig: { type: "input", allowedTypes: ["output"] }

});