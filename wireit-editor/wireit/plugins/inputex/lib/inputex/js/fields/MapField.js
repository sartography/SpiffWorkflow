(function() {
	var lang = YAHOO.lang;

	inputEx.MapFieldGlobals = {
		yahoo_preloader_error : 1,

		lat : 43.648565,
		lon : -79.385329,
		uzoom : -13,
		api : 'virtualearth',
		api_key : ''
	};

	inputEx.MapFieldZoom = {
		google : {
			to_universal : function(orig) {
				orig = parseInt(orig);
				return	Math.min(-1, -orig);
			},

			to_native : function(universal) {
				universal = parseInt(universal);
				return	universal > 0 ? universal : -universal;
			}
		},

		virtual_earth : {
			to_universal : function(orig) {
				orig = parseInt(orig);
				return	Math.min(-1, -orig);
			},

			to_native : function(universal) {
				universal = parseInt(universal);
				return	universal > 0 ? universal : -universal;
			}
		},

		yahoo : {
			to_universal : function(orig) {
				orig = parseInt(orig);
				return	Math.min(-1, orig - 18);
			},

			to_native : function(universal) {
				universal = parseInt(universal);
				return	universal > 0 ? universal : Math.max(universal + 18, 1);
			}
		}
	};

/**
 * Wrapper for Mapping APIs, including Google Maps, Yahoo Maps and Virtual Earth
 * @class inputEx.MapField
 * @extends inputEx.Field
 * @constructor
 * @param {Object} options Added options:
 * <ul>
 *    <li>width</li>
 *    <li>height</li>
 *    <li>loading</li>
 *    <li>lat</li>
 *    <li>lon</li>
 *    <li>uzoom</li>
 *    <li>api: google, yahoo or virtualearth (default)</li>
 *    <li>api_key</li>
 * </ul>
 */
inputEx.MapField = function(options) {
	inputEx.MapField.superclass.constructor.call(this,options);
};
lang.extend(inputEx.MapField, inputEx.Field, {
	/**
	 * Adds the 'inputEx-MapField' default className
	 */
	setOptions: function(options) { 
		inputEx.MapField.superclass.setOptions.call(this, options);
		this.options.className = options.className || 'inputEx-Field inputEx-MapField';
		
		this.options.width = options.width || '400px';
		this.options.height = options.height || '400px';
		this.options.loading = options.loading || 'loading....';

		this.options.lat = options.lat || inputEx.MapFieldGlobals.lat;
		this.options.lon = options.lon || inputEx.MapFieldGlobals.lon;
		this.options.uzoom = options.uzoom || inputEx.MapFieldGlobals.uzoom;
		this.options.api = options.api || inputEx.MapFieldGlobals.api;
		this.options.api_key = options.api_key || inputEx.MapFieldGlobals.api_key;
	},

	/**
	 * Render the field using the appropriate mapping function
	 */
	renderComponent: function() {
		if(inputEx.MapFieldsNumber == undefined) { inputEx.MapFieldsNumber = -1; }
		inputEx.MapFieldsNumber += 1;

		this.apid = this.virtualearth;
		if (this.options.api == "virtualearth") {
			this.apid = this.virtualearth;
		} else if (this.options.api == "google") {
			this.apid = this.google;
		} else if (this.options.api == "yahoo") {
			this.apid = this.yahoo;
		} else {
			alert("unknown API '" + this.options.api + "': using 'virtualearth'");
		}

		var id = "inputEx-MapField-"+inputEx.MapFieldsNumber;
		var idWrapper = "inputEx-MapFieldWrapper-"+inputEx.MapFieldsNumber;
		var idLat = "inputEx-MapFieldLat-"+inputEx.MapFieldsNumber;
		var idLon = "inputEx-MapFieldLon-"+inputEx.MapFieldsNumber;
		var idUZoom = "inputEx-MapFieldUZoom-"+inputEx.MapFieldsNumber;
		var idNZoom = "inputEx-MapFieldNZoom-"+inputEx.MapFieldsNumber;

		// the wrapper is needed for Virtual Earth
		this.elWrapper = inputEx.cn('div',
			{ id: idWrapper, style: "width: " + this.options.width + "; height: " + this.options.height },
			null,
			null
		);
		this.fieldContainer.appendChild(this.elWrapper);

		this.el = inputEx.cn('div',
			{ id: id, style: "position: relative; width: " + this.options.width + "; height: " + this.options.height },
			null,
			this.options.loading
		);
		this.elWrapper.appendChild(this.el);

		this.elLat = inputEx.cn('input', { id: idLat, type: "hidden", value: this.options.lat });
		this.fieldContainer.appendChild(this.elLat);

		this.elLon = inputEx.cn('input', { id: idLon, type: "hidden", value: this.options.lon });
		this.fieldContainer.appendChild(this.elLon);

		this.elUZoom = inputEx.cn('input', { id: idUZoom, type: "hidden", value: this.options.uzoom });
		this.fieldContainer.appendChild(this.elUZoom);

		this.elNZoom = inputEx.cn('input', { id: idNZoom, type: "hidden", value: this.options.uzoom });
		this.fieldContainer.appendChild(this.elNZoom);

		if (this.apid.preload(this)) {
			return;
		} else {
			this.wait_create();
		}
	},

	/**
	 * set the value: {lat: 45.23234, lon: 2.34456, uzoom: 6, nzoom: 6}
	 */
	setValue: function(value) {
		var any = false;

		if (value.uzoom != undefined) {
			this.elUZoom.value = value.uzoom;
			any = true;
		} else if (value.nzoom != undefined) {
			this.elUZoom.value = this.apid.f_zoom.to_universal(value.uzoom);
			any = true;
		}

		if (value.lat != undefined) {
			this.elLat.value = value.lat;
			any = true;
		}

		if (value.lon != undefined) {
			this.elLon.value = value.lon;
			any = true;
		}

		if (any) {
			this.apid.onposition();
		}
	},

	/**
	 * return the same structure as setValue
	 */
	getValue: function() {
		if (!this.elLat) return {};
		return {
			lat : parseFloat(this.elLat.value),
			lon : parseFloat(this.elLon.value),
			uzoom : parseInt(this.elUZoom.value),
			nzoom : parseInt(this.elNZoom.value)
		};
	},

	/**
	 *	This will wait until the DOM element appears before completion of map rendering
	 */
	wait_create : function(_this) {
		if (this == window) {
			_this.wait_create(_this);
			return;
		}

		if (document.getElementById(this.el.id)) {
			this.apid.create(this);
		} else {
			window.setTimeout(this.wait_create, 0.1, this);
		}
	},

	yahoo : {
		y_map : null,
		f_zoom : inputEx.MapFieldZoom.yahoo,

		/**
		 *	This preloaded MAY not really work -- we recommend that you use
		 *	the following JavaScript instead _after_ "yahoo-dom-event.js" (or similar)
		 *	is included:
		 *
		 *	script type="text/javascript"
		 *	YMAPPID = [yourapikey]
		 *	/script
		 *	script type="text/javascript" src="http://us.js2.yimg.com/us.js.yimg.com/lib/map/js/api/ymapapi_3_8_0_7.js"
		 *	/script
		 *
		 *	Note the non-standard loading pattern! See:
		 *	http://yuiblog.com/blog/2006/12/14/maps-plus-yui/
		 */
		preload : function(superwrapper) {
			if (window.YMap) {
				return;
			}

			if (!inputEx.MapFieldGlobals.yahoo_preloader_error) {
				inputEx.MapFieldGlobals.yahoo_preloader_error = 1;
				alert("InputEx.MapField: we do not recommend dynamic API loading for Yahoo Maps");
			}

			var preloader = 'MapYahooPreloader_' + inputEx.MapFieldsNumber;
			if (!inputEx[preloader]) {
				inputEx[preloader] = 1;

				var api_key = superwrapper.options.api_key[window.location.hostname];
				if (!api_key) {
					var api_key = superwrapper.options.api_key;
				}
				if (!api_key) {
					alert("No map key is defined for Yahoo Maps");
					return	true;
				}
				window.YMAPPID = api_key;

				var script = document.createElement("script");
				script.src = "http://us.js2.yimg.com/us.js.yimg.com/lib/map/js/api/ymapapi_3_8_0_7.js";
				script.type = "text/javascript";
		
				document.getElementsByTagName("head")[0].appendChild(script);
			}

			window.setTimeout(function() {
				if (window.YMap) {
					superwrapper.wait_create();
				} else {
					superwrapper.yahoo.preload(superwrapper);
				}
			}, 0.1);

			return	true;
		},

		create : function(superwrapper) {
			this.y_map = new YMap(superwrapper.el);
			this.y_map._mapField = superwrapper;

			this.y_map.addTypeControl();
			this.y_map.addZoomLong();
			this.y_map.addPanControl();
			this.y_map.setMapType(YAHOO_MAP_REG);

			YEvent.Capture(this.y_map, EventsList.endMapDraw, this.onposition);
			YEvent.Capture(this.y_map, EventsList.changeZoom, this.onposition);
			YEvent.Capture(this.y_map, EventsList.endPan, this.onposition);

			this.y_map.drawZoomAndCenter(
				new YGeoPoint(superwrapper.elLat.value, superwrapper.elLon.value), 
				inputEx.MapFieldZoom.yahoo.to_native(superwrapper.elUZoom.value)
			);
		},

		onposition : function() {
			try {
				var c = this.getCenterLatLon();
				this._mapField.elLat.value = c.Lat;
				this._mapField.elLon.value = c.Lon;

				var z = this.getZoomLevel();
				this._mapField.elNZoom.value = z;
				this._mapField.elUZoom.value = inputEx.MapFieldZoom.yahoo.to_universal(z);
			} catch (x) {
				//alert(x);
			}
		}
	},

	google : {
		g_map : null,
		f_zoom : inputEx.MapFieldZoom.google,


		/**
		 *	If the Google Maps API has not been explicitly loaded, this will go get
		 *	it on the user's behalf. They must have set 'api_key' to be either the API Key
		 *	for this host, or a dictionary of { window.location.hostname : api_key }.
		 *
		 *	See: http://code.google.com/apis/ajax/documentation/#Dynamic
		 */
		preload : function(superwrapper) {
			if (window.GMap2) {
				return;
			}

			var api_key = superwrapper.options.api_key[window.location.hostname];
			if (!api_key) {
				var api_key = superwrapper.options.api_key;
			}
			if (!api_key) {
				alert("No map key is defined for Google Maps");
				return	true;
			}

			var preloader = 'MapGooglePreloader_' + inputEx.MapFieldsNumber;
			inputEx[preloader] = function() {
				google.load("maps", "2", {
					"callback" : function() {
						superwrapper.wait_create();
					}
				});
			};

			if (window.google) {
				inputEx[preloader]();
			} else {
				var script = document.createElement("script");
				script.src = "http://www.google.com/jsapi?key=" + api_key + "&callback=inputEx." + preloader;
				script.type = "text/javascript";

				document.getElementsByTagName("head")[0].appendChild(script);
			}

			return	true;
		},

		create : function(superwrapper) {
			this.g_map = new GMap2(superwrapper.el);
			this.g_map._mapField = superwrapper;

			this.g_geocoder = new GClientGeocoder();
			this.g_geocoder.setBaseCountryCode("ca");

			GEvent.addListener(this.g_map, "load", this.onposition);
			GEvent.addListener(this.g_map, "moveend", this.onposition);
			GEvent.addListener(this.g_map, "zoomend", this.onposition);

			this.g_map.addControl(new GSmallMapControl());
			this.g_map.addControl(new GMapTypeControl());

			this.g_map.setCenter(
				new GLatLng(parseFloat(superwrapper.elLat.value), parseFloat(superwrapper.elLon.value)),
				inputEx.MapFieldZoom.google.to_native(superwrapper.elUZoom.value)
			);
		},

		onposition : function() {
			try {
				var c = this.getCenter();
				this._mapField.elLat.value = c.lat();
				this._mapField.elLon.value = c.lng();

				var z = this.getZoom();
				this._mapField.elNZoom.value = z;
				this._mapField.elUZoom.value = inputEx.MapFieldZoom.google.to_universal(z);
			} catch (x) {
				//alert(x);
			}
		}
	},

	virtualearth : {
		ve_map : null,
		f_zoom : inputEx.MapFieldZoom.virtualearth,

		/**
		 *	If Virtual Earth has not been added via script tag, this
		 *	will download it for you
		 *
		 *	http://soulsolutions.com.au/Blog/tabid/73/EntryID/519/Default.aspx
		 *	p_elSource.attachEvent is not a function
		 */
		preload : function(superwrapper) {
			if (window.VEMap) {
				return;
			}

			var preloader = 'MapVEPreloader_' + inputEx.MapFieldsNumber;
			inputEx[preloader] = function() {
				superwrapper.wait_create();
			};

			/*
			 *	Fixes the 'p_elSource.attachEvent is not a function' error
		 	 *	http://www.google.ca/search?hl=en&q=p_elSource.attachEvent+is+not+a+function&btnG=Google+Search&meta=
			 *	
			 */
			if (!window.attachEvent) {
				var script = document.createElement("script");
				script.src = "http://dev.virtualearth.net/mapcontrol/v6.2/js/atlascompat.js";
				script.type = "text/javascript";

				document.getElementsByTagName("head")[0].appendChild(script);
			}

			var script = document.createElement("script");
			script.src = "http://dev.virtualearth.net/mapcontrol/mapcontrol.ashx?v=6.2&onScriptLoad=inputEx." + preloader;
			script.type = "text/javascript";

			document.getElementsByTagName("head")[0].appendChild(script);

			return	true;
		},

		create : function(superwrapper) {
			superwrapper.el.style.position = "absolute";

			this.ve_map = new VEMap(superwrapper.el.id);
			this.ve_map._mapField = superwrapper;

			this.ve_map.LoadMap(
				new VELatLong(superwrapper.elLat.value, superwrapper.elLon.value),
				inputEx.MapFieldZoom.virtual_earth.to_native(superwrapper.elUZoom.value),
				VEMapStyle.Road, false, VEMapMode.Mode2D, true, 1);

			var onposition = this.onposition;
			var ve_map = this.ve_map;

			this.ve_map.AttachEvent("onendzoom", function() { onposition(ve_map); });
			this.ve_map.AttachEvent("onendpan", function() { onposition(ve_map); });

			this.onposition(this.ve_map);
		},

		onposition : function(ve_map) {
			if (!ve_map) return;
			try {
				var c = ve_map.GetCenter();
				if (!c || !c.Latitude) {
					return;
				}

				ve_map._mapField.elLat.value = c.Latitude;
				ve_map._mapField.elLon.value = c.Longitude;

				var z = ve_map.GetZoomLevel();
				ve_map._mapField.elNZoom.value = z;
				ve_map._mapField.elUZoom.value = inputEx.MapFieldZoom.virtual_earth.to_universal(z);
			} catch (x) {
				alert("MapField.virtualearth.onposition:" + x);
			}
		}
	},

	end : 0
});

// Register this class as "map" type
inputEx.registerType("map", inputEx.MapField);

})();
