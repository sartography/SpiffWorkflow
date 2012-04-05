/**
 * Ajax Adapter using a REST interface. Expect JSON response for all queries.
 * @static 
 */
WireIt.WiringEditor.adapters.RestJSON = {
	
	init: function() {
		YAHOO.util.Connect.setDefaultPostHeader('application/json; charset=utf-8');
	},
	
	saveWiring: function(val, callbacks) {
		try {
		
		// TODO/ 
		//var prev = project.editor.pipesByName[val.name];
		var method = 'PUT';
		var url = '';
		var wiring = {};
		
		if(prev) {
			YAHOO.lang.augmentObject({},  prev);
			url = '/wirings/'+prev.id+'.json';
		}
		else {
			wiring = {};
			url = '/wirings?format=json';
			method = 'POST';
		}
		
		wiring.name = val.name;
		wiring.config = val.working;
		
		var postData = YAHOO.lang.JSON.stringify({"wiring": wiring });// , 'authenticity_token':window._token });
		
		YAHOO.util.Connect.asyncRequest( method, url, {
			success: function(o) {
				var r,s;
				// TODO: store the id ?
				if( !wiring ) {
					s = o.responseText;
					r = YAHOO.lang.JSON.parse(s);
				}
				else {
					r = {};
				}
			 	callbacks.success.call(callbacks.scope, r);
			},
			failure: function(o) {
				var error = o.status + " " + o.statusText;
				callbacks.failure.call(callbacks.scope, error);
			}
		},postData);
	}catch(ex) {console.log(ex);}
	},
	
	deleteWiring: function(val, callbacks) {
		
		// TODO: 
		//var wiring = project.editor.pipesByName[val.name];
		
		var url ='/wirings/'+wiring.id+'.json';
		YAHOO.util.Connect.asyncRequest('DELETE', url, {
			success: function(o) {
			 	callbacks.success.call(callbacks.scope, {});
			},
			failure: function(o) {
				var error = o.status + " " + o.statusText;
				callbacks.failure.call(callbacks.scope, error);
			}
		});
	},
	
	listWirings: function(val, callbacks) {
		YAHOO.util.Connect.asyncRequest('GET', '/wirings.json', {
			success: function(o) {
				var s = o.responseText;
					v = YAHOO.lang.JSON.parse(s);
				var p = [];
				for(var i = 0 ; i < v.length ; i++) {
					p.push({
						id: v[i].id,
						name: v[i].name,
						working: v[i].config
					});
				}
			 	callbacks.success.call(callbacks.scope, p);
			},
			failure: function(o) {
				var error = o.status + " " + o.statusText;
				callbacks.failure.call(callbacks.scope, error);
			}
		});
	}
	
};