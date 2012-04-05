(function() {

    /**
    *
    * By Marco van Hylckama Vlieg (marco@i-marco.nl)
    *
    * THIS IS A WORK IN PROGRESS
    *
    * Many, many thanks go out to Daniel Satyam Barreiro!
    * Please read his article about YUI widget development
    * http://yuiblog.com/blog/2008/06/24/buildingwidgets/
    * Without his excellent help and advice this widget would not
    * be half as good as it is now.
    */
    
    /**
    * The accordionview module provides a widget for managing content bound to an 'accordion'.
    * @module accordionview
    * @requires yahoo, dom, event, element, animation
    */
    
    var YUD = YAHOO.util.Dom, YUE = YAHOO.util.Event, YUA = YAHOO.util.Anim;
    
    /**
    * A widget to control accordion views.
    * @namespace YAHOO.widget
    * @class AccordionView
    * @extends YAHOO.util.Element
    * @constructor
    * @param {HTMLElement | String} el The id of the html element that represents the AccordionView. 
    * @param {Object} oAttr (optional) A key map of the AccordionView's 
    * initial oAttributes.  
    */

    var AccordionView = function(el, oAttr) {
        
        el = YUD.get(el);
        
        // some sensible defaults
        
        oAttr = oAttr || {};
        if(!el) {
            el = document.createElement(this.CONFIG.TAG_NAME);
        }
        if (el.id) {oAttr.id = el.id; }
        YAHOO.widget.AccordionView.superclass.constructor.call(this, el, oAttr); 

        this.initList(el, oAttr);
                
        // This refresh forces all defaults to be set
         
        this.refresh(['id', 'width','hoverActivated'],true);  
        
    };


    /**
     * @event panelClose
     * @description Fires before a panel closes.
     * See <a href="YAHOO.util.Element.html#addListener">Element.addListener</a>
     * for more information on listening for this event.
     * @type YAHOO.util.CustomEvent
     */
    
    var panelCloseEvent = 'panelClose';

    /**
     * @event panelOpen
     * @description Fires before a panel opens.
     * See <a href="YAHOO.util.Element.html#addListener">Element.addListener</a>
     * for more information on listening for this event.
     * @type YAHOO.util.CustomEvent
     */
    
    var panelOpenEvent = 'panelOpen';
    
    /**
     * @event afterPanelClose
     * @description Fires after a panel has finished closing.
     * See <a href="YAHOO.util.Element.html#addListener">Element.addListener</a>
     * for more information on listening for this event.
     * @type YAHOO.util.CustomEvent
     */
    
    var afterPanelCloseEvent = 'afterPanelClose';
 
    /**
     * @event afterPanelOpen
     * @description Fires after a panel has finished opening.
     * See <a href="YAHOO.util.Element.html#addListener">Element.addListener</a>
     * for more information on listening for this event.
     * @type YAHOO.util.CustomEvent
     */
    
    var afterPanelOpenEvent = 'afterPanelOpen';

    /**
     * @event stateChanged
     * @description Fires after the accordion has fully changed state (after opening and/or closing (a) panel(s)).
     * See <a href="YAHOO.util.Element.html#addListener">Element.addListener</a>
     * for more information on listening for this event.
     * @type YAHOO.util.CustomEvent
     */
    
    var stateChangedEvent = 'stateChanged';
    
    /**
     * @event beforeStateChange
     * @description Fires before a state change.
     * This is useful to cancel an entire change operation
     * See <a href="YAHOO.util.Element.html#addListener">Element.addListener</a>
     * for more information on listening for this event.
     * @type YAHOO.util.CustomEvent
     */
    
    var beforeStateChangeEvent = 'beforeStateChange';

    YAHOO.widget.AccordionView = AccordionView;
    
    YAHOO.extend(AccordionView, YAHOO.util.Element, {
                
        /**
        * Initialize attributes for the Accordion
        * @param {Object} oAttr attributes key map
        * @method initAttributes
        */
        
        initAttributes: function (oAttr) {
            AccordionView.superclass.initAttributes.call(this, oAttr);
            var bAnimate = (YAHOO.env.modules.animation) ? true : false;    
            this.setAttributeConfig('id', {
                writeOnce: true,
                validator: function (value) {
                    return (/^[a-zA-Z][\w0-9\-_.:]*$/.test(value));
                },
                value: YUD.generateId(),
                method: function (value) {
                    this.get('element').id = value;
                }
            });
            this.setAttributeConfig('width', {
                value: '400px',
                method: function (value) {
                    this.setStyle('width', value);
                    }
                }
            );
            this.setAttributeConfig('animationSpeed', {
                value: 0.7
                }
            );
            this.setAttributeConfig('animate', {
                value: bAnimate,
                validator: YAHOO.lang.isBoolean
                }
            );          
            this.setAttributeConfig('collapsible', {
                value: false,
                validator: YAHOO.lang.isBoolean
                }
            );
            this.setAttributeConfig('expandable', {
                value: false,
                validator: YAHOO.lang.isBoolean
                }
            );
            this.setAttributeConfig('effect', {
                value: YAHOO.util.Easing.easeBoth,
                validator: YAHOO.lang.isString

                }
            );
            this.setAttributeConfig('hoverActivated', {
                    value: false,
                    validator: YAHOO.lang.isBoolean,
                    method: function (value) {
                            if (value) {
                                    YUE.on(this, 'mouseover', this._onMouseOver, this, true);                        
                            } else {
                                    YUE.removeListener(this, 'mouseover', this._onMouseOver);
                            }        
                    }
            });
            this.setAttributeConfig('_hoverTimeout', {
                value: 500,
                validator: YAHOO.lang.isInteger
                }
            );
        },
        
        /**
         * Configuration object containing tag names used in the AccordionView component.
         * See sourcecode for explanation in case you need to change this
         * @property CONFIG
         * @public
         * @type Object
         */
        
        CONFIG : {
          // tag name for the entire accordion
          TAG_NAME : 'UL',
          // tag name for the wrapper around a toggle + content pair
          ITEM_WRAPPER_TAG_NAME : 'LI',
          // tag name for the wrapper around the content for a panel
          CONTENT_WRAPPER_TAG_NAME : 'DIV'         
        },
 
        /**
         * Configuration object containing classes used in the AccordionView component.
         * See sourcecode for explanation in case you need to change this
         * @property CLASSES
         * @public
         * @type Object
         */
        
        CLASSES : {
            // the entire accordion
            ACCORDION : 'yui-accordionview',
            // the wrapper around a toggle + content pair
            PANEL : 'yui-accordion-panel',
            // the element that toggles a panel
            TOGGLE : 'yui-accordion-toggle',
            // the element that contains the content of a panel
            CONTENT : 'yui-accordion-content',
            // to indicate that a toggle is active
            ACTIVE : 'active',
            // to indicate that content is hidden
            HIDDEN : 'hidden',
            // the opened/closed indicator
            INDICATOR : 'indicator'                       
        },
        
        /**
        * Internal counter to make sure id's are unique
        * @property _idCounter
        * @private
        * @type Integer
        */
        
        _idCounter : '1',
        
        /**
        * Holds the timer for hover activated accordions
        * @property _hoverTimer
        * @private
        */
        
        _hoverTimer : null,      

        /**
        * Holds references to all accordion panels (list elements) in an array
        * @property _panels
        * @private
        * @type Array
        */

        _panels : null,
        
        /**
        * Keeps track of whether a panel is currently in the process of opening.
        * Used to time when a full change is finished (open and close panel)
        * @property _opening
        * @private
        * @type Boolean
        */        
        _opening : false,
        
        /**
        * Keeps track of whether a panel is currently in the process of closing.
        * Used to time when a full change is finished (open and close panel)
        * @property _closing
        * @private
        * @type Boolean
        */        
        
        _closing : false,
                
        /**
        * Whether we're running FF2 or older (or another derivate of Gecko < 1.9)
        * @property _ff2
        * @private
        * @type Boolean
        */
        
        _ff2 : (YAHOO.env.ua.gecko > 0 && YAHOO.env.ua.gecko < 1.9),

        /**
        * Whether we're running IE6 or IE7
        * @property _ie
        * @private
        * @type Boolean
        */

        _ie : (YAHOO.env.ua.ie < 8 && YAHOO.env.ua.ie > 0),

        /**
        * Whether we're ARIA capable (currently only IE8 ad FF3)
        * @property _ARIACapable
        * @private
        * @type Boolean
        */
        
        _ARIACapable : (YAHOO.env.ua.ie > 7 || YAHOO.env.ua.gecko >= 1.9),
        
        /**
        * Initialize the list / accordion
        * @param {HTMLElement} el The element for the accordion
        * @param {Object} oAttr attributes key map
        * @method initList
        * @public
        */

        initList : function(el, oAttr) {  
            YUD.addClass(el, this.CLASSES.ACCORDION);
            this._setARIA(el, 'role', 'tree');
            var aCollectedItems = [];
            var aListItems = el.getElementsByTagName(this.CONFIG.ITEM_WRAPPER_TAG_NAME);

            for(var i=0;i<aListItems.length;i++) {           
                if(YUD.hasClass(aListItems[i], 'nopanel')) {         
                    aCollectedItems.push({label: 'SINGLE_LINK', content: aListItems[i].innerHTML.replace(/^\s\s*/, '').replace(/\s\s*$/, '')});
                }
                else {
                    if(aListItems[i].parentNode === el) {
                        for (var eHeader = aListItems[i].firstChild; eHeader && eHeader.nodeType != 1; eHeader = eHeader.nextSibling) {
                        // This loop looks for the first non-textNode element
                        }
                        if (eHeader) {
                            for (var eContent = eHeader.nextSibling; eContent && eContent .nodeType != 1; eContent = eContent .nextSibling) {
                            // here we go for the second non-textNode element, if there was a first one
                            }
                        aCollectedItems.push({label: eHeader.innerHTML, content: (eContent && eContent.innerHTML)});
                        }
                    }
                }
            }
            el.innerHTML = '';
            if(aCollectedItems.length > 0) {
                this.addPanels(aCollectedItems);
            }
            
            if((oAttr.expandItem === 0) || (oAttr.expandItem > 0)) {                                   
                var eLink = this._panels[oAttr.expandItem].firstChild;
                var eContent = this._panels[oAttr.expandItem].firstChild.nextSibling;
                YUD.removeClass(eContent, this.CLASSES.HIDDEN);
                if(eLink && eContent) {
                    YUD.addClass(eLink, this.CLASSES.ACTIVE);
                    eLink.tabIndex = 0;
                    this._setARIA(eLink, 'aria-expanded', 'true');
                    this._setARIA(eContent, 'aria-hidden', 'false');
                }
            }
   
            this.initEvents();
        },
        
        /**
        * Attach all event listeners
        * @method initEvents
        * @public
        */
        
        initEvents : function() {
            
            if(true === this.get('hoverActivated')) {
                    this.on('mouseover', this._onMouseOver, this, true);        
                    this.on('mouseout', this._onMouseOut, this, true);         
            }
            
            this.on('click', this._onClick, this, true);
            this.on('keydown', this._onKeydown, this, true);
            
            // set this._opening and this._closing before open/close operations begin
            
            this.on('panelOpen', function(){this._opening = true;}, this, true);
            this.on('panelClose', function(){this._closing = true;}, this, true);
            
            // This makes sure that this._fixTabindexes is called after a change has
            // fully completed
            
            this.on('afterPanelClose', function(){
                this._closing = false;
                if(!this._closing && !this._opening) {
                    this._fixTabIndexes();
                }
            }, this, true);
            this.on('afterPanelOpen', function(){
                this._opening = false;
                if(!this._closing && !this._opening) {
                    this._fixTabIndexes();
                }
            }, this, true);
            
            /*
            This is needed when the hrefs are removed from links
            to be able to still hit enter to follow the link
            We only do this when we have ARIA support
            */
            
            if(this._ARIACapable) {
                this.on('keypress', function(ev){
                    var eCurrentPanel = YUD.getAncestorByClassName(YUE.getTarget(ev), this.CLASSES.PANEL);
                    var keyCode = YUE.getCharCode(ev);
                    if(keyCode === 13) {
                        this._onClick(eCurrentPanel.firstChild);
                        return false;
                    }
                });
            }    
        },
        
        
        /**
        * Wrapper around setAttribute to make sure we only set ARIA roles and states
        * in browsers that support it
        * @ethod _setARIA
        * @param {HTMLElement} el the element to set the attribute on
        * @param {String} sAttr the attribute name
        * @param {String} sValue the value for the attribute
        * @private
        */
        
        _setARIA : function(el, sAttr, sValue) {
            if(this._ARIACapable) {
                el.setAttribute(sAttr, sValue);
            }
        },
        
        /**
        * Closes all panels 
        * @method _collapseAccordion
        * @private
        */

        _collapseAccordion : function() {
            YUD.batch(this._panels, function(e) {
                var elContent = this.firstChild.nextSibling;
                if(elContent) { 
                    YUD.removeClass(e.firstChild, this.CLASSES.ACTIVE);
                    YUD.addClass(elContent, this.CLASSES.HIDDEN);
                    this._setARIA(elContent, 'aria-hidden', 'true');
                }
            }, this);
        },

        /**
        * Set tabIndex to 0 on the first item in case all panels are closed
        * or active. Otherwise set it to -1
        * @method _fixTabIndexes
        * @private
        */

        _fixTabIndexes : function() {
            var aLength = this._panels.length;
            var bAllClosed = true;
            for(var i=0;i<aLength;i++) {
                if(YUD.hasClass(this._panels[i].firstChild, this.CLASSES.ACTIVE)) {
                    this._panels[i].firstChild.tabIndex = 0;
                    bAllClosed = false;
                }
                else {
                    this._panels[i].firstChild.tabIndex = -1;
                }
            }
            if(bAllClosed) {
                this._panels[0].firstChild.tabIndex = 0;
            }
            // now everything is done so we can fire the stateChanged event
            this.fireEvent(stateChangedEvent);
        },

        /**
        * Adds an Accordion panel to the AccordionView instance.  
        * If no index is specified, the panel is added to the end of the tab list.
        * @method addPanel
        * @param {Object} oAttr A key map of the Panel's properties
        * @param {Integer} nIndex The position to add the tab. 
        */

        addPanel : function(oAttr, nIndex) {
            var oPanelParent = document.createElement(this.CONFIG.ITEM_WRAPPER_TAG_NAME);
            YUD.addClass(oPanelParent, this.CLASSES.PANEL);
            
            // single links that have no panel get class link and
            // no +/- indicator
            
            if(oAttr.label === 'SINGLE_LINK') {
                oPanelParent.innerHTML = oAttr.content;
                YUD.addClass(oPanelParent.firstChild, this.CLASSES.TOGGLE);
                YUD.addClass(oPanelParent.firstChild, 'link');
            }
            else {
                var elIndicator = document.createElement('span');
                YUD.addClass(elIndicator, this.CLASSES.INDICATOR);
                var elPanelLink = oPanelParent.appendChild(document.createElement('A'));
                elPanelLink.id = this.get('element').id + '-' + this._idCounter + '-label';               
                elPanelLink.innerHTML = oAttr.label || '';
                elPanelLink.appendChild(elIndicator);
                
                // if we use ARIA we remove the hrefs from links, UNLESS one has been
                // provided by the developer
                
                if(this._ARIACapable) {
                    if(oAttr.href) {
                        elPanelLink.href = oAttr.href;
                    }
                }
                else {
                    elPanelLink.href = oAttr.href || '#toggle';    
                }
                
                elPanelLink.tabIndex = -1;
                YUD.addClass(elPanelLink, this.CLASSES.TOGGLE);
                var elPanelContent = document.createElement(this.CONFIG.CONTENT_WRAPPER_TAG_NAME);
                elPanelContent.innerHTML = oAttr.content || '';
                YUD.addClass(elPanelContent, this.CLASSES.CONTENT);
                oPanelParent.appendChild(elPanelContent);
                this._setARIA(oPanelParent, 'role', 'presentation');
                this._setARIA(elPanelLink, 'role', 'treeitem');
                this._setARIA(elPanelContent, 'aria-labelledby', elPanelLink.id);
                this._setARIA(elIndicator, 'role', 'presentation');             
            }
            this._idCounter++;
            if(this._panels === null) {
                this._panels = [];
            }
            if((nIndex !== null) && (nIndex !== undefined)) {
                var ePanelBefore = this.getPanel(nIndex);
                this.insertBefore(oPanelParent, ePanelBefore);             
                var aNewPanels = this._panels.slice(0,nIndex);
                var aNewPanelsAfter = this._panels.slice(nIndex);
                aNewPanels.push(oPanelParent);
                for(i=0;i<aNewPanelsAfter.length;i++) {
                    aNewPanels.push(aNewPanelsAfter[i]);
                }
                this._panels = aNewPanels;               
            }
            else {
                this.appendChild(oPanelParent);
                if(this.get('element') === oPanelParent.parentNode) {
                    this._panels[this._panels.length] = oPanelParent;
                }
            }
            if(oAttr.label !== 'SINGLE_LINK') {
                if(oAttr.expand) {
                    if(!this.get('expandable')) {
                        this._collapseAccordion();
                    }
                    YUD.removeClass(elPanelContent, this.CLASSES.HIDDEN);
                    YUD.addClass(elPanelLink, this.CLASSES.ACTIVE);
                    this._setARIA(elPanelContent, 'aria-hidden', 'false');
                    this._setARIA(elPanelLink, 'aria-expanded', 'true');
                }
                else {
                    YUD.addClass(elPanelContent, 'hidden');
                    this._setARIA(elPanelContent, 'aria-hidden', 'true');
                    this._setARIA(elPanelLink, 'aria-expanded', 'false');
                }
            }
            var t= YAHOO.lang.later(0, this, function(){this._fixTabIndexes();this.fireEvent(stateChangedEvent);});
        },

        /**
        * Wrapper around addPanel to add multiple panels in one call
        * @method addPanels
        * @param {Array} oPanels array holding all individual panel configs
        */

        addPanels : function(oPanels) {
            for(var i=0;i<oPanels.length;i++) {
                this.addPanel(oPanels[i]);
            }
        },

        /**
        * Removes the specified Panel from the AccordionView.
        * @method removePanel
        * @param {Integer} index of the panel to be removed
        */

        removePanel : function(index) {
            this.removeChild(YUD.getElementsByClassName(this.CLASSES.PANEL, this.CONFIG.ITEM_WRAPPER_TAG_NAME, this)[index]); 
            var aNewPanels = []; 
            var nLength = this._panels.length;
            for(var i=0;i<nLength;i++) {
                if(i !== index) {
                    aNewPanels.push(this._panels[i]);
                }
            }
            this._panels = aNewPanels;
            var t= YAHOO.lang.later(0, this, function(){this._fixTabIndexes();this.fireEvent(stateChangedEvent);});
        },

        /**
        * Returns the HTMLElement of the panel at the specified index.
        * @method getPanel
        * @param {Integer} nIndex The position of the Panel.
        * @return {HTMLElement} the requested panel element
        */

        getPanel : function(nIndex) {
            return this._panels[nIndex];
        },

        /**
        * Returns the Array containing all panels
        * @method getPanels
        * @return {Array} An array with references to the panels in the correct order
        */

        getPanels : function() {
            return this._panels;
        },

        /**
        * Open a panel
        * @method openPanel
        * @param {Integer} nIndex The position of the Panel.
        * @return {Boolean} whether action resulted in opening a panel
        * that was previously closed
        */

        openPanel : function(nIndex) {
            var ePanelNode = this._panels[nIndex];
            if(!ePanelNode) {return false;} // invalid node
            if(YUD.hasClass(ePanelNode.firstChild, this.CLASSES.ACTIVE)) {return false;} // already open
            this._onClick(ePanelNode.firstChild);
            return true;
        },

        /**
        * Close a panel
        * @method closePanel
        * @param {Integer} nIndex The position of the Panel.
        * @return {Boolean} whether action resulted in closing a panel or not
        * that was previously open
        *
        * This method honors all constraints imposed by the properties collapsible and expandable
        * and will return false if the panel can't be closed because of a constraint in addition
        * to if it was already closed
        *
        */

        closePanel : function(nIndex) {
            var aItems = this._panels;
            var ePanelNode = aItems[nIndex];
            if(!ePanelNode) {return false;} // invalid node
            var ePanelLink = ePanelNode.firstChild;
            if(!YUD.hasClass(ePanelLink, this.CLASSES.ACTIVE)) {return true;} // already closed
            if(this.get('collapsible') === false) {
                if(this.get('expandable') === true) {
                    this.set('collapsible', true);
                    for(var i=0;i<aItems.length;i++) {
                        if((YUD.hasClass(aItems[i].firstChild, this.CLASSES.ACTIVE) && i !== nIndex)) {
                            this._onClick(ePanelLink);
                            this.set('collapsible', false);            
                            return true;
                        }
                    }
                    this.set('collapsible', false);                
                }
            } // can't collapse
            this._onClick(ePanelLink);
            return true;
        },

        /**
        * Keyboard event handler for keyboard control of the widget
        * @method _onKeydown
        * @param {Event} ev The Dom event
        * @private
        */

        _onKeydown : function(ev) {
            var eCurrentPanel = YUD.getAncestorByClassName(YUE.getTarget(ev), this.CLASSES.PANEL);
            var nKeyCode = YUE.getCharCode(ev);
            var nLength = this._panels.length;
            if(nKeyCode === 37 || nKeyCode === 38) {
                for(var i=0;i<nLength;i++) {
                    if((eCurrentPanel === this._panels[i]) && i>0) {
                        this._panels[i-1].firstChild.focus();
                        return;
                    } 
                }
            }
            if(nKeyCode === 39 || nKeyCode === 40) {
                for(var i=0;i<nLength;i++) {
                    if((eCurrentPanel === this._panels[i]) && i<nLength-1) {
                        this._panels[i+1].firstChild.focus();
                        return;
                    } 
                }
            }
        },

        /**
        * Mouseover event handler
        * @method _onMouseOver
        * @param {Event} ev The Dom event
        * @private
        */

        _onMouseOver : function(ev) {
            YUE.stopPropagation(ev);
            // must provide the TARGET or IE will destroy the event before we can
            // use it. Thanks Nicholas Zakas for pointing this out to me
            var target = YUE.getTarget(ev);
            this._hoverTimer = YAHOO.lang.later(this.get('_hoverTimeout'), this, function(){
                this._onClick(target);
             });
        },

        /**
        * Mouseout event handler
        * Cancels the timer set by AccordionView::_onMouseOver
        * @method _onMouseOut
        * @param {Event} ev The Dom event
        * @private
        */
        
        _onMouseOut : function() {
            if (this._hoverTimer) { 
                this._hoverTimer.cancel();
                this._hoverTimer = null;
            }
        },
        
        /**
        * Global event handler for mouse clicks
        * This method can accept both an event and a node so it can be called internally if needed
        * @method _onClick
        * @param {HTMLElement|Event} arg The Dom event or event target
        * @private
        */

        _onClick : function(arg) {
            var ev;
            if(arg.nodeType === undefined) {
                ev = YUE.getTarget(arg);
                if(!YUD.hasClass(ev, this.CLASSES.TOGGLE) && !YUD.hasClass(ev, this.CLASSES.INDICATOR)) {
                    return false;
                }
                if(YUD.hasClass(ev, 'link')) {
                    return true;
                }
                YUE.preventDefault(arg);
                YUE.stopPropagation(arg);
            }
            else {
                ev = arg;
            }

            var elClickedNode = ev;
            var that = this;
            /**
            *
            * helper function to fix IE problems with nested accordions
            * still looking for something better but for now this will have to do
            * @param {Object} el element to apply the fix to
            * @param {String} sHide whether to set visibility to hidden or visible
            *
            */

            function iehide(el, sHide) {
                if(that._ie) {
                    var aInnerAccordions = YUD.getElementsByClassName(that.CLASSES.ACCORDION, that.CONFIG.TAG_NAME, el);
                    if(aInnerAccordions[0]) {
                        YUD.setStyle(aInnerAccordions[0], 'visibility', sHide);
                    }
                }
            }

            /**
            *
            * Toggle an accordion panel
            * @param {Object} el element to toggle
            * @param {Object} elClicked the element that was clicked to toggle the corresponding panel
            *
            */

            function toggleItem(el, elClicked) {      
                var that = this;
                function fireEvent(type,panel) {
                    if (!YUD.hasClass(panel,that.CLASSES.PANEL)) {
                        panel = YUD.getAncestorByClassName(panel, that.CLASSES.PANEL);
                    }
                    for (var i = 0, p = panel; p.previousSibling; i++) {
                        p = p.previousSibling;
                    }
                    return that.fireEvent(type, {panel: panel, index: i});
                }
                      
                if(!elClicked) {
                    if(!el) { return false ;}
                    elClicked = el.parentNode.firstChild;
                }
                var oOptions = {};
                var nHeight = 0;

                var bHideAfter = (!YUD.hasClass(el, this.CLASSES.HIDDEN));

                if(this.get('animate')) {
                    if(!bHideAfter) {
                        // this eliminates a flash in Gecko < 1.9
                        if(this._ff2) {
                            YUD.addClass(el, 'almosthidden');
                            YUD.setStyle(el, 'width', this.get('width'));
                            }
                        YUD.removeClass(el, this.CLASSES.HIDDEN);
                        nHeight = el.offsetHeight;
                        YUD.setStyle(el, 'height', 0);
                        if(this._ff2) {
                            YUD.removeClass(el, 'almosthidden');
                            YUD.setStyle(el, 'width', 'auto');
                            }
                        oOptions = {height: {from: 0, to: nHeight}};
                    }
                    else {
                        nHeight = el.offsetHeight;
                        oOptions = {height: {from: nHeight, to: 0}};
                    }
                    var nSpeed = (this.get('animationSpeed')) ? this.get('animationSpeed') : 0.5;
                    var sEffect = (this.get('effect')) ? this.get('effect') : YAHOO.util.Easing.easeBoth;
                    var oAnimator = new YUA(el, oOptions, nSpeed, sEffect);
                    if(bHideAfter) {
                        if (this.fireEvent(panelCloseEvent, el) === false) { return; }
                        YUD.removeClass(elClicked, that.CLASSES.ACTIVE);
                        elClicked.tabIndex = -1;
                        iehide(el, 'hidden');
                        that._setARIA(el, 'aria-hidden', 'true');
                        that._setARIA(elClicked, 'aria-expanded', 'false');
                        oAnimator.onComplete.subscribe(function(){
                            YUD.addClass(el, that.CLASSES.HIDDEN);
                            YUD.setStyle(el, 'height', 'auto');
                            fireEvent('afterPanelClose', el);
                        });
                    }
                    else {
                        if (fireEvent(panelOpenEvent, el) === false) { return; }
                        //changed from visible to hidden so it doesn't show up behind the parent accordion until after the animation
                        iehide(el, 'hidden');
                        oAnimator.onComplete.subscribe(function(){
                            YUD.setStyle(el, 'height', 'auto');
                            //Added to make the inner accordion visible again
                            iehide(el, 'visible');
                            that._setARIA(el, 'aria-hidden', 'false');
                            that._setARIA(elClicked, 'aria-expanded', 'true');
                            elClicked.tabIndex = 0;
                            fireEvent(afterPanelOpenEvent, el);
                        });                 
                        YUD.addClass(elClicked, this.CLASSES.ACTIVE);
                    }
                    oAnimator.animate();
                }
                else {
                    if(bHideAfter) {
                        if (fireEvent(panelCloseEvent, el) === false) { return; }
                        YUD.addClass(el, that.CLASSES.HIDDEN);
                        YUD.setStyle(el, 'height', 'auto');
                        YUD.removeClass(elClicked, that.CLASSES.ACTIVE);
                        that._setARIA(el, 'aria-hidden', 'true');
                        that._setARIA(elClicked, 'aria-expanded', 'false');
                        elClicked.tabIndex = -1;
                        fireEvent(afterPanelCloseEvent, el);
                    }
                    else {
                        if (fireEvent(panelOpenEvent, el) === false) { return; }
                        YUD.removeClass(el, that.CLASSES.HIDDEN);
                        YUD.setStyle(el, 'height', 'auto');
                        YUD.addClass(elClicked, that.CLASSES.ACTIVE);
                        that._setARIA(el, 'aria-hidden', 'false');
                        that._setARIA(elClicked, 'aria-expanded', 'true');
                        elClicked.tabIndex = 0;
                        fireEvent(afterPanelOpenEvent, el);
                    }
                }
                return true;
            }
            var eTargetListNode = (elClickedNode.nodeName.toUpperCase() === 'SPAN') ? elClickedNode.parentNode.parentNode : elClickedNode.parentNode;

            var containedPanel = YUD.getElementsByClassName(this.CLASSES.CONTENT, this.CONFIG.CONTENT_WRAPPER_TAG_NAME, eTargetListNode)[0]; 
            if (this.fireEvent(beforeStateChangeEvent, this) === false) { return; }
            if(this.get('collapsible') === false) {
                if (!YUD.hasClass(containedPanel, this.CLASSES.HIDDEN)) {
                    return false;
                }
            }
            else {
                if(!YUD.hasClass(containedPanel, this.CLASSES.HIDDEN)) {
                    toggleItem.call(this, containedPanel);
                    return false;               
                }
            }
                    
            if(this.get('expandable') !== true) {
                var nLength = this._panels.length;
                for(var i=0; i<nLength; i++) {
                    var bMustToggle = YUD.hasClass(this._panels[i].firstChild.nextSibling, this.CLASSES.HIDDEN);
                    if(!bMustToggle) {
                        toggleItem.call(this,this._panels[i].firstChild.nextSibling);
                    }
                }
            }
            
            if(elClickedNode.nodeName.toUpperCase() === 'SPAN')  {
                toggleItem.call(this, containedPanel, elClickedNode.parentNode);
            }
            else {
                toggleItem.call(this, containedPanel, elClickedNode);
            }
            return true;
        },
       
        /**
        * Provides a readable name for the AccordionView instance.
        * @method toString
        * @return {String} String representation of the object 
        */
        
        toString : function() {
            var name = this.get('id') || this.get('tagName');
            return "AccordionView " + name; 
        }
    });    
})();
YAHOO.register("accordionview", YAHOO.widget.AccordionView, {version: "0.99", build: "33"});