(function() {

    var util= YAHOO.util,
        Dom = util.Dom,
        Event = util.Event,
        widget = YAHOO.widget,

		sRoleButtonTemplate = '<button type="button">role: none</button>',		
		sBodyRoleButtonTemplate = '<button id="body-button" type="button">role: none</button>',
        txt = 'Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Maecenas sit amet metus. Nunc quam elit, posuere nec, auctor in, rhoncus quis, dui. Aliquam erat volutpat. Ut dignissim, massa sit amet dignissim cursus, quam lacus feugiat.',

		oHeaderRoleButton,
		oBodyRoleButton,
		oFooterRoleButton;


    util.GridBuilder = {

        init: function() {
           
           util.GridBuilder.propertiesPanel = new inputEx.widget.Dialog({
        			inputExDef: {
        			         type: 'form',
     			            fields: [ 
     			                        {type:'string', label: 'Title', name: 'title', required: true },
     											{type:'string', label: 'Header', name: 'header', required: true },
     											{type:'string', label: 'Footer', name: 'footer', required: true }
     										],
     			            buttons: [
     			               {type: 'button', value: 'Save', onClick: function() { 
     			                  util.GridBuilder.setPageProperties(util.GridBuilder.propertiesPanel.getForm().getValue());
     								}},
     			               {type: 'button', value: 'Cancel', onClick: function() { util.GridBuilder.propertiesPanel.hide(); } }
     			            ]
        			      },
        			title: 'Page informations',
        			panelConfig: {
        				constraintoviewport: true, 
        				underlay:"shadow", 
        				close:true, 
        				fixedcenter: true,
        				visible:false, 
        				draggable:true,
        				modal: true
        			}
        	});

         this.yqlPanel = new widget.Panel('yqlHolder', {
		            close: true,
		            visible: false,
        				modal: true,
		            width: '950px',
		            fixedcenter: true
		        }
		    );
    		 this.yqlPanel.render(document.body);
		    
		    this.templatesPanel = new widget.Panel('templatesHolder', {
 		            close: true,
 		            visible: false,
         			modal: true,
 		            width: '950px',
 		            fixedcenter: true
 		        }
 		    );
    		 this.templatesPanel.render(document.body);


          inputEx.spacerUrl = "http://neyric.github.com/inputex/images/space.gif";
		    this.templates = new inputEx.ListField({
    			listLabel: 'Templates',
    			elementType: {type: 'text', rows: 5, cols: 60 },
    			value: ['\n{for p in query.results.results.photo}\n	  <a href="http://farm${p.farm}.static.flickr.com/${p.server}/${p.id}_${p.secret}_b.jpg"><img src="http://farm${p.farm}.static.flickr.com/${p.server}/${p.id}_${p.secret}_s.jpg"></a>\n{/for}'], 
    			parentEl: 'templatesContainer',
    			useButtons: true
    		});
		    

		    this.toolBox = new widget.Panel('toolBoxHolder', {
		            close: true,
		            visible: false,
		            xy: [10, 10],
		            width: '235px'
		        }
		    );

		    this.toolBox.render(document.body);

			this.hd = Dom.get('hd');
         this.bd = Dom.get('bd');
			this.ft = Dom.get('ft');
	
	         this.titleStr = "A flickr example";
            this.headerStr = this.hd.firstChild.innerHTML;
            this.footerStr = this.ft.firstChild.innerHTML;
            this.headerDefault = this.headerStr;
            this.footerDefault = this.footerStr;
            this.type = 'yui-t7';
            this.docType = 'doc';
            this.rows = [];
            this.rows[0] = Dom.get('splitBody0');
            this.storeCode = false;
            this.sliderData = false;

            this.doc = Dom.get('doc');
            this.template = Dom.get('which_grid');

            Event.on(this.template, 'change', util.GridBuilder.changeType, util.GridBuilder, true);
            Event.on('splitBody0', 'change', util.GridBuilder.splitBody, util.GridBuilder, true);
            Event.on('which_doc', 'change', util.GridBuilder.changeDoc, util.GridBuilder, true);
            Event.on(this.bd, 'mouseover', util.GridBuilder.mouseOver, util.GridBuilder, true);

            var code_button = new widget.Button('show_code');
            code_button.on('click', util.GridBuilder.showCode, util.GridBuilder, true);
            
            var test_button = new widget.Button('test');
            test_button.on('click', util.GridBuilder.test, util.GridBuilder, true);

            var reset_button = new widget.Button('resetBuilder');
            reset_button.on('click', util.GridBuilder.reset, util.GridBuilder, true);

            var add_button = new widget.Button('addRow');
            add_button.on('click', util.GridBuilder.addRow, util.GridBuilder, true);

            var show_button = new widget.Button('showGridBuilder');
            show_button.on('click', util.GridBuilder.toolBox.show, util.GridBuilder.toolBox, true);
            
            var properties_button = new widget.Button('setProperties');
            properties_button.on('click', util.GridBuilder.openPropertiesPanel, util.GridBuilder, true);
            
            var yql_button = new widget.Button('showYqlEditor');
            yql_button.on('click', util.GridBuilder.showYqlEditor, util.GridBuilder, true);
            
            var templates_button = new widget.Button('showTemplatesEditor');
            templates_button.on('click', util.GridBuilder.showTemplatesEditor, util.GridBuilder, true);
            
            var save_button = new widget.Button('save');
            save_button.on('click', util.GridBuilder.save, util.GridBuilder, true);
            
            
            this.tooltip = new widget.Tooltip('classPath', { context: 'bd', showDelay:500 } );

			//	Prevent tooltips on Buttons, Menus, and reading order indicators
			this.tooltip.subscribe("contextMouseOver", function (type, args) {

				var oEvent = args[1],
					oTarget = Event.getTarget(oEvent);
				
				return !(Dom.hasClass(oTarget, "yui-button") || 
							Dom.getAncestorByClassName(oTarget, "yui-button") || 
							Dom.hasClass(oTarget, "yuimenu") || 
							Dom.getAncestorByClassName(oTarget, "yuimenu") || 
							Dom.hasClass(oTarget, "order-indicator"));
				
			});


			this.ariaCheckbox = Dom.get("use-aria");
			this.useARIA = this.ariaCheckbox.checked;

			if (this.useARIA) {
				this.initARIA();
			}

			Event.on("use-aria", "click", this.toggleARIA, null, this);


			this.orderCheckbox = Dom.get("show-order");
			this.showOrder = this.orderCheckbox.checked;

			if (this.showOrder) {
				this.createReadingOrderBadges();
			}

			Event.on("show-order", "click", this.toggleOrderBadges, null, this);

			this.splitBody();
			
			this.load();

        },
        
		initARIA: function () {

			this.hd.setAttribute("role", "banner");
            this.bd.setAttribute("role", "main");
			this.ft.setAttribute("role", "contentinfo");
			
			this.createRoleButtons();
			
		},

		toggleARIA: function (event) {

			this.useARIA = this.ariaCheckbox.checked;

			//	Need to remove and re-add the reading order badges because 
			//	toggling the ARIA role buttions can cause the reading order 
			//	badges to appear in the wrong place

			if (this.showOrder) {
				this.removeReadingOrderBadges();
			}

			if (this.useARIA) {
				this.createRoleButtons();
			}
			else {
				this.destroyRoleButtons();
			}

			if (this.showOrder) {
				this.createReadingOrderBadges();
			}
			
		},

		setRole: function (event) {

			var oMenuItem = event.newValue,
				sRole = oMenuItem.cfg.getProperty("text"),
				oDIV = Dom.getAncestorByTagName(this.get("element"), "div");


			this.set("label", ("role: " + sRole));
			this.set("value", sRole);


			if (sRole === "none") {
				oDIV.removeAttribute("role");
			}
			else if (sRole) {
				oDIV.setAttribute("role", sRole);
			}

		},

		createRoleButton: function (el) {

			var aRoles = [
					"none",
					"application",
					"banner",
					"complementary",
					"contentinfo",
					"main",
					"navigation",
					"search"
				];

			var oButton = new widget.Button(el, { type: "menu", menu: aRoles, lazyloadmenu: false });
			oButton.on("selectedMenuItemChange", this.setRole);
 			
			var sRole = Dom.getAncestorByTagName(oButton.get("element"), "div").getAttribute("role");
			
			if (sRole) {
				oButton.set("value", sRole);
			}

			var nRoles = aRoles.length,
				i = nRoles - 1;
			
			do {

				if (sRole === aRoles[i]) {
					oButton.set("selectedMenuItem", oButton.getMenu().getItem(i));
					break;
				}
				
			}
			while (i--);

			return oButton;
			
		},

		createHeaderRoleButton: function () {

			this.hd.innerHTML = '<button id="header-button" type="button">role: banner</button>' + this.hd.innerHTML;
			oHeaderRoleButton = this.createRoleButton("header-button");
			
		},
		
		createFooterRoleButton: function () {

			this.ft.innerHTML = '<button id="footer-button" type="button">role: contentinfo</button>' + this.ft.innerHTML;
			oFooterRoleButton = this.createRoleButton("footer-button");
			
		},

		createBodyRoleButtons: function () {

			var aParagraphs = this.bd.getElementsByTagName("p");

			if (aParagraphs.length > 1) {

				Dom.batch(aParagraphs, function (element) {
					element.innerHTML = sRoleButtonTemplate + element.innerHTML;
				});

			}

			this.bd.innerHTML = (sBodyRoleButtonTemplate + this.bd.innerHTML);

			var aButtonEls = this.bd.getElementsByTagName("button"),
				nButtonEls = aButtonEls.length,
				aBodyRoleButtons = [],
				i;
			
			if (nButtonEls > 0) {

				for (i = 0; i < nButtonEls; i++) {
					aBodyRoleButtons.push(this.createRoleButton(aButtonEls[i]));
				}

			}

			oBodyRoleButton = widget.Button.getButton("body-button");
			
			this.bodyRoleButtons = aBodyRoleButtons;
			
		},
		
		destroyBodyRoleButtons: function () {

			var aRoleButtons = this.bodyRoleButtons,
				nRoleButtons,
				i;


			if (aRoleButtons) {
				
				nRoleButtons = aRoleButtons.length;


				if (nRoleButtons > 0) {
					
					i = nRoleButtons - 1;
					
					do {
						aRoleButtons[i].destroy();
					}
					while (i--);
					
				}
				
				this.bodyRoleButtons = null;
				
			}
			
		},

		createRoleButtons: function () {

			this.createHeaderRoleButton();
			this.createBodyRoleButtons();
			this.createFooterRoleButton();
			
		},
		
		destroyRoleButtons: function () {
			
			oHeaderRoleButton.destroy();
			this.destroyBodyRoleButtons();
			oFooterRoleButton.destroy();
			
		},

		applyRolesToBody: function (bodyHTML) {

			//	Temporarily remove the role buttons from the body of the grid
			this.destroyBodyRoleButtons();

			//	Grid Builder wraps each row of the grid's body in a helper <div>
			//	(e.g. <div id="gridBuilder1">).  This helper <div> is not part
			//	of the HTML template returned by the call to the "doTemplate" 
			//	method.  In order to compare the <div>s in the grid's body to 
			//	those generated by the call to the "doTemplate" method it is 
			//	nessary to create new a collection of <div>s that exclude the 
			//	helper <div>s.


			var aDIVs = Dom.getElementsBy(function (element) {

				//	The helper <div>s have no class name, only an id, whereas 
				//	the <div>s used by YUI Grids, have a class applied.  
				//	Therefore, purge the helper <div>s.
				
				return !(element.id && element.id.indexOf("gridBuilder") === 0);
	
			}, "div", this.bd);


			var sBodyHTML = bodyHTML,
				i = 0;


			var addRole = function (str) {

				var oDIV = aDIVs[i],
					sRole,
					sReturnValue = str;

				if (oDIV) {

					sRole = oDIV.getAttribute("role");

					if (sRole) {
						sReturnValue = str + 'role="' + sRole + '" ';
					}
					
				}

				i++;

				return sReturnValue;

			};


			if (aDIVs && aDIVs.length > 0) {

				//	Compare each <div> element in the body of the grid to each <div>
				//	in the HTML template created by the call to the "doTemplate" 
				//	method, applying a landmark role to each <div> in the template  
				//	whose position is the same as the corresponding <div> in the 
				//	body of the grid.

				sBodyHTML = sBodyHTML.replace(/<div /gi, addRole);

			}

			//	Place the role buttons back into the body of the grid
			this.createBodyRoleButtons();
			
			return sBodyHTML;
			
		},

		saveLandmarksState: function () {

			var aButtons = this.bodyRoleButtons,
				nButtons = aButtons.length,
				oSelectedMenuItem,
				aSelected = [],
				i; 
			
			for (i = 0; i < nButtons; i++) {
				oSelectedMenuItem = aButtons[i].get("selectedMenuItem");
				aSelected.push(oSelectedMenuItem ? oSelectedMenuItem.index : 0);
			}

			this.bodyLandmarks = aSelected;
			
		},

		restoreLandmarksState: function () {

			var oButton,
				aSelected = this.bodyLandmarks,
				nSelected = aSelected.length,
				i;

			if (aSelected) {

				for (i = 0; i < nSelected; i++) {

					oButton = this.bodyRoleButtons[i];

					if (oButton) {
						oButton.set("selectedMenuItem", oButton.getMenu().getItem(aSelected[i]));
					}

				}
				
			}
			
		},

		toggleOrderBadges: function (event) {
			
			this.showOrder = this.orderCheckbox.checked;
			
			if (this.showOrder) {
				this.createReadingOrderBadges();
			}
			else {
				this.removeReadingOrderBadges();
			}
			
		},

		createReadingOrderBadges: function () {

			var aPs = this.bd.getElementsByTagName("p"),
				nPs = aPs.length,
				oDIV = document.createElement("div");
			
			var createOrderBadge = function (order, element) {
				
				oDIV.innerHTML = '<div class="order-indicator"> Order ' + order + '</div>';
				element.appendChild(oDIV.firstChild);
				
			};
			

			createOrderBadge(1, this.hd);
			createOrderBadge(nPs+2, this.ft);
			

			for (var i = 0; i < nPs; i++) {
				createOrderBadge((i+2), aPs[i]);
			}
			
		},
		
		removeReadingOrderBadges: function () {

 			Dom.getElementsByClassName("order-indicator", "div", this.doc, function (element) {

				element.parentNode.removeChild(element);
	
			});
			
		},

        reset: function(ev) {

            for (var i = 1; i < this.rows.length; i++) {
                if (this.rows[i]) {
                    if (Dom.get('splitBody' + i)) {
                        Dom.get('splitBody' + i).parentNode.parentNode.removeChild(Dom.get('splitBody' + i).parentNode);
                    }
                }
            }
            this.rows = [];
            this.rows[0] = Dom.get('splitBody0');
            Dom.get('which_doc').options.selectedIndex = 0;
            Dom.get('which_grid').options.selectedIndex = 0;
            Dom.get('splitBody0').options.selectedIndex = 0;

            this.hd.innerHTML = '<h1>' + this.headerDefault + '</h1>';
            this.ft.innerHTML = '<p>' + this.footerDefault + '</p>';

            this.headerStr = this.headerDefault;
            this.footerStr = this.footerDefault;

            this.changeDoc();
            this.changeType();
            this.splitBody();

			if (this.useARIA) {
				this.destroyBodyRoleButtons();
				this.initARIA();
			}

            Event.stopEvent(ev);
        },

        addRow: function(ev) {

			if (this.useARIA) {
				this.saveLandmarksState();
			}

            var oSelect = Dom.get('splitBody0').cloneNode(true);
            oSelect.id = 'splitBody' + this.rows.length;

            this.rows[this.rows.length] = oSelect;
            this.rowCounter++;

            var oDIV = document.createElement('div');
            oDIV.innerHTML = '<button type="button" class="rowDel" id="gridRowDel' + this.rows.length + '">Remove this row</button><label>Row:</label>';
            oDIV.lastChild.appendChild(oSelect);

			var oParentNode = Dom.get('splitBody0').parentNode.parentNode.parentNode;
            oParentNode.insertBefore(oDIV, Dom.get("addRow"));

            Event.on(oSelect, 'change', util.GridBuilder.splitBody, util.GridBuilder, true);
            Event.on('gridRowDel' + this.rows.length, 'click', util.GridBuilder.delRow, util.GridBuilder, true);

            this.splitBody();

			if (this.useARIA) {

				//	If a right or left "nav"/sidebar column was inserted into  
				//	the grid after the state was saved, then it is necessary to 
				//	inject a new element into the cache of body landmarks roles  
				//	to represent the newly added column.  Because this column  
				//	will always be the last element in the body, it is inserted  
				//	into that position.
				if (this.template.selectedIndex > 0 && this.bodyLandmarks.length > 1) {
					this.bodyLandmarks.splice((this.bodyLandmarks.length - 1), 0, 0);
				}

				this.restoreLandmarksState();
			}

			if (YAHOO.env.ua.ie) {
				this.toolBox.sizeUnderlay();
			}
			
            Event.stopEvent(ev);
        },

        delRow: function(ev) {

			if (this.useARIA) {
				this.saveLandmarksState();
			}
	
            var tar = Event.getTarget(ev);
            var id = tar.id.replace('gridRowDel', '');

            Dom.get('splitBody0').parentNode.parentNode.parentNode.removeChild(tar.parentNode);

            this.rows[id] = false;

            this.splitBody();

			if (this.useARIA) {
				this.restoreLandmarksState();
			}

			if (YAHOO.env.ua.ie) {
				this.toolBox.sizeUnderlay();
			}

            Event.stopEvent(ev);
        },

        changeDoc: function(ev) {	// Body Size

			if (this.useARIA) {
				this.saveLandmarksState();
			}

			this.prevDocType = this.currentDocType;
			this.currentDocType = Dom.get('which_doc').selectedIndex;
            this.docType = Dom.get('which_doc').options[this.currentDocType].value;

            if (this.docType == 'custom-doc') {
                this.showSlider();
            } else {
                this.doc.style.width = '';
                this.doc.style.minWidth = '';
                this.sliderData = false;
                this.doc.id = this.docType;
                this.doTemplate();
            }
            if (ev) {
                Event.stopEvent(ev);
            }

			if (this.useARIA) {
				this.restoreLandmarksState();
			}

        },

        changeType: function() {	//	Body Columns

			if (this.useARIA) {
				this.saveLandmarksState();
			}
	
            this.type = this.template.options[this.template.selectedIndex].value;
            this.doc.className = this.type;
            this.doTemplate();

			if (this.useARIA) {
				this.restoreLandmarksState();
			}

        },

        doTemplate: function(lorem) {
            if (this.storeCode) {
                this.splitBody();
            }
            var html = '';
            var str = '<p>' + txt + '</p>';
            var navStr = '<p class="nav">' + txt + '</p>';
            if (lorem) {
                str = txt;
                navStr = txt;
            } else if (this.storeCode) {
                str = '<!-- YOUR DATA GOES HERE -->';
                navStr = '<!-- YOUR NAVIGATION GOES HERE -->';
            }
            if (this.bodySplit) {
                if (lorem) {
                    str = this.bodySplit.replace(/\{0\}/g, txt);
                } else if (this.storeCode) {
                    str = this.bodySplit.replace(/\{0\}/g, "\t" + '<!-- YOUR DATA GOES HERE -->\n\t<div class="yourData"></div>' + "\n\t");
                } else {
                    str = this.bodySplit.replace(/\{0\}/g, '<p>' + txt + '</p>');
                }
            }

			if (this.type === 'yui-t7') {
                 html = str;				
			}
			else {
                 html = '<div id="yui-main">' + "\n\t" + '<div class="yui-b">' + str + '</div>' + "\n\t" + '</div>' + "\n\t" + '<div class="yui-b">' + navStr + '</div>' + "\n\t";				
			}

            if (this.storeCode) {
                return html;
            } else {

				if (this.showOrder) {
					this.removeReadingOrderBadges();
				}

				if (this.useARIA) {
					this.destroyBodyRoleButtons();
				}

                this.bd.innerHTML = html;

				if (this.useARIA) {
					this.createBodyRoleButtons();
				}

				if (this.showOrder) {
					//	Need to pause for a second otherwise the order badges
					//	will appear in the wrong place
					YAHOO.lang.later(0, this, this.createReadingOrderBadges);
				}

            }
        },

        PixelToEmStyle: function(size, prop) {
            var data = '';
            prop = ((prop) ? prop.toLowerCase() : 'width');
            var sSize = (size / 13);
            data += prop + ':' + (Math.round(sSize * 100) / 100) + 'em;';
            data += '*' + prop + ':' + (Math.round((sSize * 0.9759) * 100) / 100) + 'em;';
            if ((prop == 'width') || (prop == 'height')) {
                data += 'min-' + prop + ':' + size + 'px;';
            }
            return data;
        },

        getCode: function(lorem) {

			if (this.showOrder) {
				this.removeReadingOrderBadges();
			}

            this.storeCode = true;
            var css = "";
            if (this.sliderData) {
                if (this.sliderData.indexOf('px') != -1) {
                    css = '#custom-doc { ' + this.PixelToEmStyle(parseInt(this.sliderData, 10)) + ' margin:auto; text-align:left; }';
                } else {
                    css = '#custom-doc { width: ' + this.sliderData + '; min-width: 250px; }';
                }
            }
            
            css += "#hd { padding: 5px; background-color: #CCCCCC; color: white; }\n"+
                   "#hd h1 { font-size: 32pt; }\n"+
                   "#bd { border:1px solid #CCCCCC; }\n"+
                   "#ft { padding: 10px 10px 0; background-color: #CCCCCC; color: black; -moz-border-radius-bottomleft: 10px; -moz-border-radius-bottomright:10px;}\n";

            var code = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"' + "\n" + ' "http://www.w3.org/TR/html4/strict.dtd">' + "\n";
            code += '<html>' + "\n";
            code += '<head>' + "\n";
            code += '   <title>'+this.titleStr+'</title>' + "\n";
            code += '   <link rel="stylesheet" href="http:/'+'/yui.yahooapis.com/' + YAHOO.VERSION + '/build/reset-fonts-grids/reset-fonts-grids.css" type="text/css">' + "\n";
            code += '   <link rel="stylesheet" href="http:/'+'/yui.yahooapis.com/' + YAHOO.VERSION + '/build/base/base.css" type="text/css">' + "\n";
            code += '   <style type="text/css">' + "\n";
            code += css + "\n";
            code += '   </style>' + "\n";
            code += '</head>' + "\n";
            code += '<body>' + "\n";
            code += '<div id="' + this.docType + '" class="' + this.type + '">' + "\n";


			var sHeaderRole,
				sHeaderRoleAttr = "",
				sBodyRole,
				sBodyRoleAttr = "",
				sFooterRole,
				sFooterRoleAttr = "",
				sBodyHTML = this.doTemplate(lorem);



			if (this.useARIA) {

				sHeaderRole = oHeaderRoleButton.get("value");
				sHeaderRoleAttr = sHeaderRole === "none" ? "" : ' role="' + oHeaderRoleButton.get("value") + '"';

				sBodyRole = oBodyRoleButton.get("value");
				sBodyRoleAttr = sBodyRole === "none" ? "" : ' role="' + oBodyRoleButton.get("value") + '"';

				sFooterRole = oFooterRoleButton.get("value");
				sFooterRoleAttr = sFooterRole === "none" ? "" : ' role="' + oFooterRoleButton.get("value") + '"';

				sBodyHTML = this.applyRolesToBody(sBodyHTML);

			}

            code += '   <div id="hd"' + sHeaderRoleAttr + '><h1>' + this.headerStr + '</h1></div>' + "\n";
            code += '   <div id="bd"' + sBodyRoleAttr + '>' + "\n\t" + sBodyHTML + "\n\t" + '</div>' + "\n";
            code += '   <div id="ft"' + sFooterRoleAttr + '><p>' + this.footerStr + '</p></div>' + "\n";


            code += '</div>' + "\n";
            
            code += '<script type="text/javascript" src="http://yui.yahooapis.com/' + YAHOO.VERSION + '/build/utilities/utilities.js"></script>\n';
            code += '<script src="http://github.com/neyric/inputex/raw/master/js/inputex.js"  type="text/javascript"></script>\n';
				code += '<script src="http://github.com/neyric/inputex/raw/master/js/rpc/yql.js"  type="text/javascript"></script>\n';
            code += '<script type="text/javascript" src="http://trimpath.googlecode.com/files/trimpath-template-1.0.38.js"></script>\n';


				code += '\n\n<!-- Scripts with type="text/yql" will run on the Yahoo! YQL platform -->\n';
				code += '<script type="text/yql">\n';
				code += jsmin("", Dom.get('codeContainer').value ,2)+"\n";
				code += '</script>\n\n\n';


            code += '<script type="text/javascript">\n';
            code += 'YAHOO.util.Event.onDOMReady(function () {\n';
				code += '    inputEx.YQL.initTrimpathPage(); \n';
            code += '});\n';
            code += '</script>\n';
            code += '</body>' + "\n";
            code += '</html>' + "\n";

				// Replace  "<!-- YOUR DATA GOES HERE -->" with the i th template
				var templates = this.templates.getValue();
				var templateIndex = 0;
				while( code.indexOf('<!-- YOUR DATA GOES HERE -->') != -1) {
					code = code.replace('<!-- YOUR DATA GOES HERE -->', '<script type="text/trimpath" src="#0">'+templates[templateIndex]+'</script>');
					templateIndex += 1;
				}

            this.storeCode = false;

			if (this.showOrder) {
				this.createReadingOrderBadges();
			}

            return code;
        },

        showCode: function(ev) {

			var oPanel = this.codePanel;

			if (!oPanel) {
			
				oPanel = new widget.Panel('showCode', {
	                    close: true,
	                    draggable: true,
	                    modal: true,
	                    visible: false,
	                    fixedcenter: true,
	                    height: '382px',
	                    width: '650px'
	                }
	            );
				
	            oPanel.setHeader('CSSGridBuilder Code');
				oPanel.setBody("placeholder");
	            oPanel.setFooter('<input type="checkbox" id="includeLorem" value="1"> <label for="includeLorem">Include Lorem Ipsum text</label>');

				oPanel.body.style.overflow = "auto";
	
            	oPanel.render(document.body);	

                Event.on('includeLorem', 'click', function(ev) {

                    var check = Dom.get('includeLorem');
                    var holder = Dom.get('codeHolder');
                    var table = holder.previousSibling;
                    table.parentNode.removeChild(table);
                    var code = this.getCode(check.checked);
                    holder.style.visibility = 'hidden';
                    holder.style.display = 'block';
                    holder.value = code;
                    window.setTimeout(function() {

						oPanel.body.style.overflow = "";

                        dp.SyntaxHighlighter.HighlightAll('code');

						oPanel.body.style.overflow = "auto";

                    }, 5);

                }, this, true);

				this.codePanel = oPanel;

			}

            oPanel.setBody('<form><textarea name="code" id="codeHolder" class="HTML">' + this.getCode() + '</textarea></form>');
			oPanel.show();

            dp.SyntaxHighlighter.HighlightAll('code');

            Event.stopEvent(ev);
        },
        
        test: function(ev) {
           Event.stopEvent(ev);
			  var p = window.open("","");
     	     p.document.write( this.getCode(false/*true*/) );
     	     p.document.close();
        },
        
        runYQL: function() {
           
           if(!this.jsontreeContainer) {
              this.jsontreeContainer = Dom.get('jsontreeContainer');
           }
           
          this.jsontreeContainer.innerHTML = "<img src='http://yui.yahooapis.com/2.8.0/build/assets/skins/sam/ajax-loader.gif'/>";
          var that= this;
          
          // Minify the javascript (urls are limited....)
    	    var codeMin = jsmin("", Dom.get('codeContainer').value ,2);
          
     		 inputEx.YQL.queryCode( codeMin , function(o) {
     				that.jsontreeContainer.innerHTML = "";
     				new inputEx.widget.JsonTreeInspector('jsontreeContainer', o);
     				that.o = o;
     		   });
           
        },
        
        showTemplatesEditor: function() {
           this.templatesPanel.show();
           
       	  if(this.o) {
       	     Dom.get('templateJsontreeContainer').innerHTML = "";
       	     new inputEx.widget.JsonTreeInspector('templateJsontreeContainer', this.o.query.results);
       	  }
           
        },
        
        showYqlEditor: function() {
           this.yqlPanel.show();
        },
        
        openPropertiesPanel: function() {
           var form = this.propertiesPanel.getForm();

           form.setValue({
              title: this.titleStr,
              header: this.headerStr,
              footer: this.footerStr
           });

          this.propertiesPanel.show(); 
        },
        
        save: function() {
           var config = {
              code: Dom.get('codeContainer').value,
              templates: this.templates.getValue(),
              properties: this.propertiesPanel.getForm().getValue()
           };
           Dom.get('link').innerHTML = "<img src='http://yui.yahooapis.com/2.8.0/build/assets/skins/sam/ajax-loader.gif'/>";
           Permalink.getTiny(config , function(tinyurl){
              var a = Dom.get('link');
              a.href=tinyurl;
              a.innerHTML = tinyurl;
           });
        },
        
        load: function() {
           var loadConfig = Permalink.load();
           
           if(loadConfig.code) {
              Dom.get('codeContainer').value = loadConfig.code;
           }
           if(loadConfig.templates) {
              this.templates.setValue(loadConfig.templates);
           }
           if(loadConfig.properties) {
              this.setPageProperties(loadConfig.properties);
           }
           
        },

        
        setPageProperties: function(config) {
           
           if (this.showOrder) {
					this.removeReadingOrderBadges();
				}

				if (this.useARIA) {
					oHeaderRoleButton.destroy();
				}
				
				this.titleStr = config.title;
	
               this.headerStr = config.header;
               this.hd.innerHTML = '<h1>' + config.header + '</h1>';
               
               this.footerStr = config.footer;
                this.ft.innerHTML = '<p>' + config.footer + '</p>';

				if (this.useARIA) {
					this.createHeaderRoleButton();
				}

				if (this.showOrder) {
					this.createReadingOrderBadges();
				}
           
           this.propertiesPanel.hide();
           
        },

        splitBody: function() {
            this.bodySplit = '';
            for (var i = 0; i < this.rows.length; i++) {
                this.splitBodyTemplate(Dom.get('splitBody' + i));
            }
            if (!this.storeCode) {
                this.doTemplate();
            }
        },

        splitBodyTemplate: function(tar) {
            if (tar) {
                var bSplit  = tar.options[tar.selectedIndex].value;
                var str = '';
                switch (bSplit) {
                    case '1':
                        str += '<div class="yui-g">' + "\n";
                        str += '{0}';
                        str += '</div>' + "\n";
                        break;
                    case '2':
                        str += '<div class="yui-g">' + "\n";
                        str += '    <div class="yui-u first">' + "\n";
                        str += '{0}';
                        str += '    </div>' + "\n";
                        str += '    <div class="yui-u">' + "\n";
                        str += '{0}';
                        str += '    </div>' + "\n";
                        str += '</div>' + "\n";
                        break;
                    case '3':
                        str += '    <div class="yui-gb">' + "\n";
                        str += '        <div class="yui-u first">' + "\n";
                        str += '{0}';
                        str += '        </div>' + "\n";
                        str += '        <div class="yui-u">' + "\n";
                        str += '{0}';
                        str += '        </div>' + "\n";
                        str += '        <div class="yui-u">' + "\n";
                        str += '{0}';
                        str += '        </div>' + "\n";
                        str += '    </div>' + "\n";
                        break;
                    case '4':
                        str += '<div class="yui-g">' + "\n";
                        str += '    <div class="yui-g first">' + "\n";
                        str += '        <div class="yui-u first">' + "\n";
                        str += '{0}';
                        str += '        </div>' + "\n";
                        str += '        <div class="yui-u">' + "\n";
                        str += '{0}';
                        str += '        </div>' + "\n";
                        str += '    </div>' + "\n";
                        str += '    <div class="yui-g">' + "\n";
                        str += '        <div class="yui-u first">' + "\n";
                        str += '{0}';
                        str += '        </div>' + "\n";
                        str += '        <div class="yui-u">' + "\n";
                        str += '{0}';
                        str += '        </div>' + "\n";
                        str += '    </div>' + "\n";
                        str += '</div>' + "\n";
                        break;
                    case '5':
                        str += '<div class="yui-g">' + "\n";
                        str += '    <div class="yui-u first">' + "\n";
                        str += '{0}';
                        str += '    </div>' + "\n";
                        str += '    <div class="yui-g">' + "\n";
                        str += '        <div class="yui-u first">' + "\n";
                        str += '{0}';
                        str += '        </div>' + "\n";
                        str += '        <div class="yui-u">' + "\n";
                        str += '{0}';
                        str += '        </div>' + "\n";
                        str += '    </div>' + "\n";
                        str += '</div>' + "\n";
                        break;
                    case '6':
                        str += '<div class="yui-g">' + "\n";
                        str += '    <div class="yui-g first">' + "\n";
                        str += '        <div class="yui-u first">' + "\n";
                        str += '{0}';
                        str += '        </div>' + "\n";
                        str += '        <div class="yui-u">' + "\n";
                        str += '{0}';
                        str += '        </div>' + "\n";
                        str += '    </div>' + "\n";
                        str += '    <div class="yui-u">' + "\n";
                        str += '{0}';
                        str += '    </div>' + "\n";
                        str += '</div>' + "\n";
                        break;
                    case '7':
                        str += '<div class="yui-gc">' + "\n";
                        str += '    <div class="yui-u first">' + "\n";
                        str += '{0}';
                        str += '    </div>' + "\n";
                        str += '    <div class="yui-u">' + "\n";
                        str += '{0}';
                        str += '    </div>' + "\n";
                        str += '</div>' + "\n";
                        break;
                    case '8':
                        str += '<div class="yui-gd">' + "\n";
                        str += '    <div class="yui-u first">' + "\n";
                        str += '{0}';
                        str += '    </div>' + "\n";
                        str += '    <div class="yui-u">' + "\n";
                        str += '{0}';
                        str += '    </div>' + "\n";
                        str += '</div>' + "\n";
                        break;
                    case '9':
                        str += '<div class="yui-ge">' + "\n";
                        str += '    <div class="yui-u first">' + "\n";
                        str += '{0}';
                        str += '    </div>' + "\n";
                        str += '    <div class="yui-u">' + "\n";
                        str += '{0}';
                        str += '    </div>' + "\n";
                        str += '</div>' + "\n";
                        break;
                    case '10':
                        str += '<div class="yui-gf">' + "\n";
                        str += '    <div class="yui-u first">' + "\n";
                        str += '{0}';
                        str += '    </div>' + "\n";
                        str += '    <div class="yui-u">' + "\n";
                        str += '{0}';
                        str += '    </div>' + "\n";
                        str += '</div>' + "\n";
                        break;
                }
                if (!this.storeCode) {
                    this.bodySplit += '<div id="gridBuilder' + (this.rows.length - 1) + '">' + str + '</div>';
                } else {
                    this.bodySplit += str;
                }
            }
        },

        mouseOver: function(ev) {
            var elm = Event.getTarget(ev);
            var path = [];
            var cont = true;
            while (cont) {
                if (elm.tagName.toLowerCase() == 'body') {
                    cont = false;
                    break;
                }
                if (elm.className) {
                    path[path.length] = elm.className;
                }
                if (elm.parentNode) {
                    elm = elm.parentNode;
                } else {
                    cont = false;
                }
            }
            this.tooltip.cfg.setProperty('text','body.' + document.body.className + ' #' + this.docType + ': ' + path.reverse().join(' : '));
        },

        showSlider: function() {

			var oDialog = this.customWidthDialog,
				oSlider = this.customWidthSlider;

            var handleSave = function() {

                this.sliderData = Dom.get('sliderValue').value;
                oDialog.hide();

            };

			var handleCancel = function () {

				Dom.get('which_doc').selectedIndex = this.prevDocType;
				this.changeDoc();
				
                oDialog.hide();
				
			};

            var handleChange = function(f) {

				var w, pix;

                if (typeof f == 'object') { f = oSlider.getValue(); }
                if (Dom.get('moveTypePercent').checked) {
                    w = Math.round(f / 2);
                    Dom.get('custom-doc').style.width = w + '%';
                    Dom.get('sliderValue').value = w + '%';
                } else {
                    w = Math.round(f / 2);
                    pix = Math.round(Dom.getViewportWidth() * (w / 100));
                    Dom.get('custom-doc').style.width = pix + 'px';
                    Dom.get('sliderValue').value = pix + 'px';
                }
                Dom.get('custom-doc').style.minWidth = '250px';
            };

            var handleBlur = function() {
                var f = Dom.get('sliderValue').value;
                if (f.indexOf('%') != -1) {
                    Dom.get('moveTypePercent').checked = true;
                    f = (parseInt(f, 10) * 2);
                } else if (f.indexOf('px') != -1) {
                    Dom.get('moveTypePixel').checked = true;
                    f = (((parseInt(f, 10) / Dom.getViewportWidth()) * 100) * 2);
                } else {
                    Dom.get('sliderValue').value = '100%';
                    f = 200;
                }
                oSlider.setValue(f);
            };


			if (!oDialog) {
				
	            oDialog = new widget.Dialog('showSlider', {
	                    close: true,
	                    draggable: true,
	                    modal: true,
	                    visible: false,
	                    fixedcenter: true,
	                    width: '275px',
	                    postmethod: 'none'
	                }
	            );

				oDialog.cfg.queueProperty("buttons", [
	                { text:'Save', handler: { fn: handleSave, scope: this }, isDefault: true },
	                { text:'Cancel', handler: { fn: handleCancel, scope: this } }
	            ]);

	            oDialog.setHeader('CSSGridBuilder Custom Body Size');

	            var body = '<p>Adjust the slider below to adjust your body size or set it manually with the text input. <i>(Be sure to include the % or px in the text input)</i></p>';
	            body += '<form name="customBodyForm" method="POST" action="">';
	            body += '<p>Current Setting: <input type="text" id="sliderValue" value="100%" size="8" onfocus="this.select()" /></p>';
	            body += '<span>Unit: ';
	            body += '<input type="radio" name="movetype" id="moveTypePercent" value="percent" checked> <label for="moveTypePercent">Percent</label>&nbsp;';
	            body += '<input type="radio" name="movetype" id="moveTypePixel" value="pixel"> <label for="moveTypePixel">Pixel</label></span>';
	            body += '</form>';
	            body += '<div id="sliderbg"><div id="sliderthumb"><img src="thumb-n.gif" /></div>';
	            body += '</div>';

	            oDialog.setBody(body);
				
			    oDialog.render(document.body);

	            oSlider = widget.Slider.getHorizSlider('sliderbg', 'sliderthumb', 0, 200, 1);

	            oSlider.onChange = handleChange;

				this.customWidthSlider = oSlider;

	            Event.on(['moveTypePercent', 'moveTypePixel'], 'click', handleChange);
	            Event.on('sliderValue', 'blur', handleBlur);	
				
				this.customWidthDialog = oDialog;
				
			}

			this.customWidthSlider.setValue(200);
			oDialog.show();

            this.doc.id = this.docType;
            this.doc.style.width = '100%';
            this.doTemplate();
        }
    };
})();
YAHOO.register("gridbuilder", YAHOO.util.GridBuilder, {version: "@VERSION@", build: "@BUILD@"});
