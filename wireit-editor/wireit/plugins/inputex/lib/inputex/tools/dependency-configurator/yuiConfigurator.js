YAHOO.namespace("yui");

YAHOO.yui.configurator = function(container) {

    var Y = YAHOO, D = Y.util.Dom, E = Y.util.Event, Button = Y.widget.Button, buttons = [],
        allModules, loadOptionalButton, filterGroup, allowRollupButton, outputTabs;

	//allow preloading via querystring:
	var baseHref = document.location.href.split("#")[0];
	var qs = (baseHref.split("?").length > 1) ? baseHref.split("?")[1].split("&") : [];
	if(!qs.indexOf) {
		qs.indexOf = function(s){
			for(var i=0; i<this.length; i++){
				if(this[i]==s){
					return i;
				}
			}
			return -1;
		};
	}
	
    function keys(o) {
        var a=[], i;
        for (i in o) {
            if (Y.lang.hasOwnProperty(o, i)) {
                a.push(i);
            }
        }

        return a;
    };

    function createButton(label) {
		 if(!YAHOO.yui.moduleMeta[label]) {
			 throw new Error("no module called "+label);
  		 }
	
        var b = new Button({
            id: label,
            type: "checkbox",
            name: label,
			checked: ((qs.indexOf(label) > -1) ? true : false),
            label: YAHOO.yui.moduleMeta[label].name,
            value: label,
            container: YAHOO.yui.moduleMeta[label].type + "Container" 
        });

        b.on("click", showDependencies);

        buttons[label] = b;
    }

    function showDependencies() {

        var reqs = [], base, filter, loadOptional, allowRollup, comboHandler;

        var o = D.get('baseInput');

        base = o && o.value;
        if (base) {
            base = Y.lang.trim(base);
        }
        loadOptional = loadOptionalButton.get('checked');
        allowRollup = allowRollupButton.get('checked');
        comboHandler = comboHandlerButton.get('checked') && !base;
        filter = filterGroup.get('value') || "MIN";

        for (var i in buttons) {
            if (Y.lang.hasOwnProperty(buttons, i)) {
                if (buttons[i].get('checked')) {
                    reqs.push(i);
                }
            }
        }

        var loader = new Y.util.YUILoader({
			combine: true,
            require: reqs,
            filter: filter,
            loadOptional: loadOptional,
            allowRollup: allowRollup,
            force: allModules
        });
        
        YAHOO.addInputExModules(loader, '../inputex/master/');

        if (base) {
            loader.base = base;
        }

        loader.calculate();
		

        var s = loader.sorted, 
			len = s.length, 
			m, 
			url, 
			out = [],
			js = [],
			css = [],
			target, 
			startLen = js.length,
			i,
			type = loader.loadType;

        if (len && !comboHandler) {

            for (i=0; i<len; i=i+1)  {
                m = loader.moduleInfo[s[i]];
                if (m.type == 'css') {
                    url = m.fullpath || loader._url(m.path);
                    out.push('<link rel="stylesheet" type="text/css" href="' + url + '">');
                }
            }

            if (out.length) {
                if (out.length < len) {
                    out.push('<!-- Individual YUI and inputEx JS files -->');
                }
                out.unshift('<!-- Individual YUI and inputEx CSS files -->');
            } else {
                out.push('<!-- Individual YUI and inputEx JS files -->');
            }

            for (i=0; i<len; i=i+1)  {
                m = loader.moduleInfo[s[i]];
                if (m.type == 'js') {
					url = m.fullpath || loader._url(m.path);
					out.push('<script type="text/javascript" src="' + url + '"></scr' + 'ipt>');						
                }
            }
        } else {//combohandling

			for (i=0; i<len; i=i+1) {

				m = loader.moduleInfo[s[i]];

				if (m && !m.ext && (!type || type === m.type)) {

					target = loader.root + m.path;
					
					if (m.type == 'js') {
						js.push(loader._filter(target));
					} else {
						css.push(target);
					}
				}
			}
			
			if (css.length) {
				out.push('<!-- Combo-handled YUI CSS files: -->');
				out.push('<link rel="stylesheet" type="text/css" href="' + loader.comboBase + css.join('&') + '">');
			}
			if (js.length) {
				out.push('<!-- Combo-handled YUI JS files: -->');
				out.push('<script type="text/javascript" src="' + loader.comboBase + js.join('&') + '"></scr' + 'ipt>');
			}
			
		}
        

		//FOR USING YUI LOADER AS A SEED FILE:
		
		var o = {}; //template contents for substitute
		
		//URL for the YUI Loader file:
		o.yuiloadersrc = loader._filter(loader.base + 'yuiloader/yuiloader-min.js');
		
		//other configs:
		o.modules = '["' + reqs.join('","') + '"]';
		o.loadOptional = loadOptional.toString();
		o.filter = (filter) ? '"' + filter + '"' : '"MIN"';
		o.allowRollup = allowRollup.toString();
		o.combine = comboHandler.toString();
		o.base = D.get('baseInput').value;
	
        
		if(out.join('\n').length > 5) {
			
			// Show syntax highlighted output for frontloading script and CSS:
        	D.get('loaderOutput').value = out.join('\n') + '\n\n';	
			
			//build the template for Loader syntax:
			var t = '<!--Include YUI Loader: -->\n<script type="text/javascript" src="{yuiloadersrc}"></scr' + 'ipt>\n\n';
			t += '<!--Include inputEx Loader: -->\n<script type="text/javascript" src="/path/to/inputex/js/inputex-loader.js"></scr' + 'ipt>\n\n';
			t += '<!--Use YUI Loader to bring in your other dependencies: -->\n<script type="text/javascript">\n';
			t += '// Instantiate and configure YUI Loader:\n(function() {\n	var loader = new YAHOO.util.YUILoader({\n';
			t += '		base: "{base}",\n';
			t += '		require: {modules},\n';
			t += '		loadOptional: {loadOptional},\n';
			t += '		combine: {combine},\n';
			t += '		filter: {filter},\n';
			t += '		allowRollup: {allowRollup},\n';
			t += '		onSuccess: function() {\n';
			t += '			//you can make use of all requested YUI modules\n';
			t += '			//here.\n';
			t += '		}\n	});\n\n';
			t += '      // Add the inputEx module references to the loader.\n';
			t += '      YAHOO.addInputExModules(loader, \'/path/to/inputex/\');\n\n';
			t += '      // Load the files using the insert() method.\n';
			t += '      loader.insert();\n';
			t += '})();\n';
			t += '</scr' + 'ipt>\n\n';
			
			/*
			var loader = new YAHOO.util.YUILoader({
         				    require: ["inputex-emailfield", "inputex-urlfield", "inputex-selectfield", "inputex-form"],
         				    loadOptional: true,
         						//base: "../lib/yui/", // remove the comment if you want to load YUI locally
         				    onSuccess: init
         				});

         				YAHOO.addInputExModules(loader, '../');
         				loader.insert();
         
         */
			
			//output for dynamically loading everything with YUI Loader:
			D.get('loaderOutputDynamic').value = YAHOO.lang.substitute(t, o);
		}
		
		//create a reusable link to this configuration:
		if(reqs.length) {
		   var baseUrl = window.location.protocol+"//"+window.location.hostname+(window.location.port != "" ? ":"+window.location.port : "");
			var configUrl = baseUrl + window.location.pathname+ "?" + reqs.join("&");
			if (filter) {
				configUrl += "&" + filter;
			}
			if (loadOptional) {
				configUrl += "&loadOptional";	
			}
			if (!comboHandler) {
				configUrl += "&nocombine";	
			}
			if (!allowRollup) {
				configUrl += "&norollup";	
			}
			if (D.get('baseInput').value.length > 0) {
				configUrl += "&basepath&";
				configUrl += D.get('baseInput').value;
			}
			if (cdnGroup.get("value") === "google") {
				configUrl += "&google";	
			}
			D.get("configUrl").innerHTML = "<strong>Bookmark or mail this configuration:</strong> <a href='" + configUrl + "'>" + configUrl + "</a>";	
		}
		
		// This syntax highlighter just keeps making new elements if you need
        // to refresh the content.  Remove existing to unbreak this.
        var oldout = D.getElementsByClassName('dp-highlighter', 'div', 'configurator');
        if (oldout && oldout.length > 1) {
            var el = oldout[0];
            el.parentNode.removeChild(el);
            var el = oldout[1];
            el.parentNode.removeChild(el);
        }
		
		dp.SyntaxHighlighter.HighlightAll('loaderOutput');
		
    }

    function init() {
		
        filterGroup = new Y.widget.ButtonGroup({id:  "filter", name:  "filter", container:  "filterContainer"});	

        filterGroup.addButtons([
            /*{ label: "-min", value: "", checked: ((qs.indexOf("DEBUG") === -1) && (qs.indexOf("RAW") === -1)) ? true : false },
            { label: "-debug", value: "DEBUG", checked: ((qs.indexOf("DEBUG") > -1) ? true : false) }, 
            { label: "raw", value: "RAW", checked: ((qs.indexOf("RAW") > -1) ? true : false)}*/
            
            { label: "-min", value: "", checked: false },
            { label: "-debug", value: "DEBUG", checked: false }, 
            { label: "raw", value: "RAW", checked: true }
        ]);
		
		function onFilterChange() {
			//when setting filter to anything other than min,
			//rollups should be turned off -- all rollups are
			//minified:
			if (this.get("value")) {
				allowRollupButton.set("checked", false);	
			}
		}
		
		//set value:
		var filter;
		if(qs.indexOf("DEBUG") > -1) {
			filter = "DEBUG";
		} else {
			if(qs.indexOf("RAW") > -1) {
				filter = "RAW";	
			} else {
				filter = "";
			}
		}
		filterGroup.set("value", filter);

        filterGroup.on("valueChange", onFilterChange);
        filterGroup.on("valueChange", showDependencies);

		//CDN Settings
        cdnGroup = new Y.widget.ButtonGroup({id:  "cdn", name:  "cdn", container:  "cdnContainer"});	

        cdnGroup.addButtons([
            { label: "Yahoo!", value: "yahoo", checked: ((qs.indexOf("google") > -1) ? false : true), title: "Note: Yahoo's CDN supports combo-handling, but it does not support SSL.  Yahoo's CDN includes YUI version 2.2.0 and later." },
            { label: "Google", value: "google", checked:  ((qs.indexOf("google") > -1) ? true : false), title:"Note: Google's CDN does not support combo-handling, but it does support SSL.  Google's CDN includes version 2.6.0 and later."}
        ]);
		
		function oncdnChange() {
			//currently, these buttons control the basepath:
			if (this.get("value") == "yahoo") {
				comboHandlerButton.set("disabled", false);
				D.get("baseInput").value = "";
			} else {
				//set path for Google:
				comboHandlerButton.set("disabled", true);
				D.get("baseInput").value = "http://ajax.googleapis.com/ajax/libs/yui/" + YAHOO.env.getVersion("yahoo").version + "/build/";
			}
		}

		//set value:
		var cdn;
		if(qs.indexOf("google") > -1) {
			cdn = "google";
		} else {
			cdn = "yahoo";
		}
		cdnGroup.set("value", cdn);

        cdnGroup.on("valueChange", oncdnChange);
        cdnGroup.on("valueChange", showDependencies);
		
        loadOptionalButton = new Button({
            id: "loadOptional",
            type: "checkbox",
            name: "loadOptional",
            label: "Load Optional",
            value: "true",
            container: "loadOptionalContainer",
			checked: true//((qs.indexOf("loadOptional") > -1) ? true : false)
        });

        loadOptionalButton.on("click", showDependencies);
		
        comboHandlerButton = new Button({
            id: "comboHandler",
            type: "checkbox",
            name: "comboHandler",
            label: "Combine Files",
            value: "true",
			checked: false,//((qs.indexOf("nocombine") > -1) ? false : true),
            container: "loadOptionalContainer" 
        });

        comboHandlerButton.on("click", showDependencies);

        allowRollupButton = new Button({
            id: "allRollup",
            type: "checkbox",
            name: "allowRollup",
            label: "Allow Rollup",
            value: "true",
            checked: false,//((qs.indexOf("norollup") > -1) ? false : true),
            container: "allowRollupContainer" 
        });
		
		allowRollupButton.on("checkedChange", function(o) {
			//if rollups are being turned on, minified files
			//will be used (rollups are minified):
			if(o.newValue) {
				filterGroup.check(0);	
			}
		});

        allowRollupButton.on("click", showDependencies);
		
		//preload the basepath if present in URL:
		if(qs.indexOf("basepath") > -1) {
			if (qs[qs.indexOf("basepath") + 1].length > 0) {
				D.get('baseInput').value = qs[qs.indexOf("basepath") + 1];
				comboHandlerButton.set("disabled", true);
			}
		}
		
		//Combo handle only when using default yahooapis base:
		E.on('baseInput', 'change', function(e) {
			if(D.get('baseInput').value.length) {
				comboHandlerButton.set("disabled", true);
			} else {
				comboHandlerButton.set("disabled", false);				
			}
			showDependencies();
		});
		

        var loader = new Y.util.YUILoader();
        
          YAHOO.addInputExModules(loader, '../inputex/master/');
          try {

        allModules = keys(loader.moduleInfo);
        allModules.sort();

        for (var i=0; i<allModules.length; i=i+1) {
            createButton(allModules[i]);
        }

        showDependencies();
        
     } catch(ex) {
        console.log(ex);
     }
		
		//Jog for IE7:
		D.setStyle("outputTabs", "position", "relative");
		D.setStyle("outputTabs", "position", "static");
		
    }
    E.onDOMReady(init);
	
	//create the Tab control for output:
	E.onAvailable("outputTabs", function() {
		outputTabs = new YAHOO.widget.TabView("outputTabs");
	});		


};
