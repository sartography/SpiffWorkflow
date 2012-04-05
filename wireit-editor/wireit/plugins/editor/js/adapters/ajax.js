/**
 * Ajax Adapter. Expect JSON response for all queries.
 * @class WireIt.WiringEditor.adapters.Ajax
 * @static 
 */
WireIt.WiringEditor.adapters.Ajax = {
	
	/**
	 * You can configure this adapter to different schemas.
	 * TIP: "url" can be a function !
	 */
	config: {
		saveWiring: {
			method: 'POST',
			url: 'saveWiring'
		},
		deleteWiring: {
			method: 'DELETE',
			url: 'deleteWiring'
		},
		listWirings: {
			method: 'GET',
			url: 'listWirings'
		}
	},
	
	/**
	 * init the adapter 
	 * @method init
	 * @static
	 */
	init: function() {
		YAHOO.util.Connect.setDefaultPostHeader('application/json');
	},
	
	/**
	 * called when saved
	 * @method saveWiring
	 * @static
	 */
	saveWiring: function(val, callbacks) {
		this._sendRequest("saveWiring", val, callbacks);
	},
	
	/**
	 * called when deleted
	 * @method deleteWiring
	 * @static
	 */
	deleteWiring: function(val, callbacks) {
		this._sendRequest("deleteWiring", val, callbacks);
	},
	
	/**
	 * called to load the wirings
	 * @method listWirings
	 * @static
	 */
	listWirings: function(val, callbacks) {
		this._sendRequest("listWirings", val, callbacks);
	},
	
	/**
	 * send a request in JSON
	 * @method _sendRequest
	 * @static
	 */
	_sendRequest: function(action, value, callbacks) {
	
		var params = [];
		for(var key in value) {
			if(value.hasOwnProperty(key)) {
				params.push(window.encodeURIComponent(key)+"="+window.encodeURIComponent(value[key]));
			}
		}
		var postData = params.join('&');
		
		var url = "";
		if( YAHOO.lang.isFunction(this.config[action].url) ) {
			url = this.config[action].url(value);
		}
		else {
			url = this.config[action].url;
		}
		
		var method = "";
		if( YAHOO.lang.isFunction(this.config[action].url) ) {
			method = this.config[action].method(value);
		}
		else {
			method = this.config[action].method;
		}

		YAHOO.util.Connect.initHeader("Content-Type", "application/x-www-form-urlencoded");
		YAHOO.util.Connect.asyncRequest(method, url, {
			success: function(o) {
				var s = o.responseText,
					 r = YAHOO.lang.JSON.parse(s);
			 	callbacks.success.call(callbacks.scope, r);
			},
			failure: function(o) {
				var error = o.status + " " + o.statusText;
				callbacks.failure.call(callbacks.scope, error);
			}
		},postData);
	}
	
};
