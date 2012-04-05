/*global YAHOO */
/**
 * WireIt provide classes to build wirable interfaces
 * @module WireIt
 */
/**
 * @class WireIt
 * @static
 * @namespace WireIt
 */
var WireIt = {
	
	
	/** 
	 * TODO
	 */
	
	defaultWireClass: "WireIt.BezierWire",
	
	wireClassFromXtype: function(xtype) {
		return this.classFromXtype(xtype, this.defaultWireClass);
	},
	
	
	defaultTerminalClass: "WireIt.Terminal",
	
	terminalClassFromXtype: function(xtype) {
		return this.classFromXtype(xtype, this.defaultTerminalClass);
	},
	

	defaultContainerClass: "WireIt.Container",
	
	containerClassFromXtype: function(xtype) {
		return this.classFromXtype(xtype, this.defaultContainerClass);
	},
	
	/**
	 * default
	 */
	classFromXtype: function(xtype, defaultXtype) {
		var path = (xtype || defaultXtype).split('.');
		var klass = window;
		for(var i = 0 ; i < path.length ; i++) {
			klass = klass[path[i]];
		}
		
      if(!YAHOO.lang.isFunction(klass)) {
         throw new Error("WireIt unable to find klass from xtype: '"+xtype+"'");
      }

		return klass;
	},
   
   /**
    * Get a css property in pixels and convert it to an integer
    * @method getIntStyle
    * @namespace WireIt
    * @static
    * @param {HTMLElement} el The element
    * @param {String} style css-property to get
    * @return {Integer} integer size
    */
   getIntStyle: function(el,style) {
      var sStyle = YAHOO.util.Dom.getStyle(el, style);
      return parseInt(sStyle.substr(0, sStyle.length-2), 10);
   },

   /**
    * Helper function to set DOM node attributes and style attributes.
    * @method sn
    * @static
    * @param {HTMLElement} el The element to set attributes to
    * @param {Object} domAttributes An object containing key/value pairs to set as node attributes (ex: {id: 'myElement', className: 'myCssClass', ...})
    * @param {Object} styleAttributes Same thing for style attributes. Please use camelCase for style attributes (ex: backgroundColor for 'background-color')
    */
   sn: function(el,domAttributes,styleAttributes){
      if(!el) { return; }
		var i;
      if(domAttributes){
         for(i in domAttributes){
				if(domAttributes.hasOwnProperty(i)) {
					var domAttribute = domAttributes[i];
	            if(typeof (domAttribute)=="function"){continue;}
	            if(i=="className"){
	               i="class";
	               el.className=domAttribute;
	            }
	            if(domAttribute!==el.getAttribute(i)){
	               if(domAttribute===false){
	                  el.removeAttribute(i);
	               }else{
	                  el.setAttribute(i,domAttribute);
	               }
	            }
				}
         }
      }
      if(styleAttributes){
         for(i in styleAttributes){
				if(styleAttributes.hasOwnProperty(i)) {
					if(typeof (styleAttributes[i])=="function"){ continue; }
					if(el.style[i]!=styleAttributes[i]){
						el.style[i]=styleAttributes[i];
					}
				}
         }
      }
   
   },


   /**
    * Helper function to create a DOM node. (wrapps the document.createElement tag and the inputEx.sn functions)
    * @method cn
    * @static
    * @param {String} tag The tagName to create (ex: 'div', 'a', ...)
    * @param {Object} [domAttributes] see inputEx.sn
    * @param {Object} [styleAttributes] see inputEx.sn
    * @param {String} [innerHTML] The html string to append into the created element
    * @return {HTMLElement} The created node
    */
   cn: function(tag, domAttributes, styleAttributes, innerHTML){
      var el=document.createElement(tag);
      this.sn(el,domAttributes,styleAttributes);
      if(innerHTML){ el.innerHTML = innerHTML; }
      return el;
   },
   
   /**
    * indexOf replace Array.indexOf for cases where it isn't available (IE6 only ?)
    * @method indexOf
    * @static
    * @param {Any} el element to search for
    * @param {Array} arr Array to search into
    * @return {Integer} element index or -1 if not found
    */
   indexOf: YAHOO.lang.isFunction(Array.prototype.indexOf) ? 
                        function(el, arr) { return arr.indexOf(el);} : 
                        function(el, arr) {
                           for(var i = 0 ;i < arr.length ; i++) {
                              if(arr[i] == el) {return i;}
                           }
                           return -1;
                        },

   /**
    * compact replace Array.compact for cases where it isn't available
    * @method compact
    * @static
    * @param {Array} arr Array to compact
    * @return {Array} compacted array
    */
   compact: YAHOO.lang.isFunction(Array.prototype.compact) ? 
                        function(arr) { return arr.compact();} :          
                        function(arr) {
                           var n = [];
                           for(var i = 0 ; i < arr.length ; i++) {
                              if(arr[i]) {
                                 n.push(arr[i]);
                              }
                           }
                           return n;
                        }
};


/**
 * WireIt.util contains utility classes
 */
WireIt.util = {};
