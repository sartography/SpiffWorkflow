/*global YAHOO,WireIt,G_vmlCanvasManager,document */
(function () {
   
   // Shortcuts
   var Event = YAHOO.util.Event, UA = YAHOO.env.ua;

   /**
    * Create a canvas element and wrap cross-browser hacks to resize it
    * @class CanvasElement
    * @namespace WireIt
    * @constructor
    * @param {HTMLElement} parentNode The canvas tag will be append to this parent DOM node.
    */
   WireIt.CanvasElement = function(parentNode) {
      
      /**
       * The canvas element
       * @property element
       * @type HTMLElement
       */
      this.element = document.createElement('canvas');
      
      // Append to parentNode
      parentNode.appendChild(this.element);
      
      // excanvas.js for dynamic canvas tags
      if(typeof (G_vmlCanvasManager)!="undefined"){
         this.element = G_vmlCanvasManager.initElement(this.element);
      }
      
   };
   
   WireIt.CanvasElement.prototype = {
      
      /**
       * Get a drawing context
       * @method getContext
       * @param {String} [mode] Context mode (default "2d")
       * @return {CanvasContext} the context
       */
      getContext: function(mode) {
       return this.element.getContext(mode || "2d");
      },
      
      /**
       * Purge all event listeners and remove the component from the dom
       * @method destroy
       */
      destroy: function() {
         var el = this.element;

         // Remove from DOM
         if(YAHOO.util.Dom.inDocument(el)) {
            el.parentNode.removeChild(el);
         }

         // recursively purge element
         Event.purgeElement(el, true);
      },
      
      /**
       * Set the canvas position and size.
       * <b>Warning:</b> This method changes the <i>element</i> property under some brother. Don't copy references !
       * @method SetCanvasRegion
       * @param {Number} left Left position
       * @param {Number} top Top position
       * @param {Number} width New width
       * @param {Number} height New height
       */
      SetCanvasRegion: UA.ie ? 
               // IE
               function(left,top,width,height){
                  var el = this.element;
                  WireIt.sn(el,null,{left:left+"px",top:top+"px",width:width+"px",height:height+"px"});
                  el.getContext("2d").clearRect(0,0,width,height);
                  this.element = el;
               } : 
               ( (UA.webkit || UA.opera) ? 
                  // Webkit (Safari & Chrome) and Opera
                  function(left,top,width,height){
                     var el = this.element;
                     var newCanvas=WireIt.cn("canvas",{className:el.className || el.getAttribute("class"),width:width,height:height},{left:left+"px",top:top+"px"});
                     var listeners=Event.getListeners(el);
                     for(var listener in listeners){
								if(listeners.hasOwnProperty(listener)) {
									var l=listeners[listener];
									Event.addListener(newCanvas,l.type,l.fn,l.obj,l.adjust);
								}
                     }
                     Event.purgeElement(el);
                     el.parentNode.replaceChild(newCanvas,el);
                     this.element = newCanvas;
                  } :  
                  // Other (Firefox)
                  function(left,top,width,height){
                     WireIt.sn(this.element,{width:width,height:height},{left:left+"px",top:top+"px"});
                  })
   };
   
})();