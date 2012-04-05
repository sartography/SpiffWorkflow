// Smaller version of gears_init.js
(function() {
	
	// We are already defined. Hooray!
   if (window.google && google.gears) {
		return;
	}

	var factory = null;

	// Firefox
	  if (typeof GearsFactory != 'undefined') {
	    factory = new GearsFactory();
	  } else {
	    // IE
	    try {
	      factory = new ActiveXObject('Gears.Factory');
	      // privateSetGlobalObject is only required and supported on IE Mobile on
	      // WinCE.
	      if (factory.getBuildInfo().indexOf('ie_mobile') != -1) {
	        factory.privateSetGlobalObject(this);
	      }
	    } catch (e) {
	      // Safari
	      if ((typeof navigator.mimeTypes != 'undefined')
	           && navigator.mimeTypes["application/x-googlegears"]) {
	        factory = document.createElement("object");
	        factory.style.display = "none";
	        factory.width = 0;
	        factory.height = 0;
	        factory.type = "application/x-googlegears";
	        document.documentElement.appendChild(factory);
	      }
	    }
	  }

	  // *Do not* define any objects if Gears is not installed. This mimics the
	  // behavior of Gears defining the objects in the future.
	  if (!factory) {
	    return;
	  }

	  // Now set up the objects, being careful not to overwrite anything.
	  //
	  // Note: In Internet Explorer for Windows Mobile, you can't add properties to
	  // the window object. However, global objects are automatically added as
	  // properties of the window object in all browsers.
	  if (!window.google) {
	    google = {};
	  }

	  if (!google.gears) {
	    google.gears = {factory: factory};
	  }
})();

/**
 * Gears Adapter (using http://gears.google.com)
 * @class WireIt.WiringEditor.adapters.Gears
 * @static 
 */
WireIt.WiringEditor.adapters.Gears = {
	
	config: {
		dbName: 'database-test'
	},
	
	init: function() {
		this.db = google.gears.factory.create('beta.database');
		this.db.open(this.config.dbName);
		this.db.execute('create table if not exists wirings (name text, working text, language text)');
	},
	
	saveWiring: function(val, callbacks) {
		var rs = this.db.execute('select * from wirings where name=? and language=?', [val.name, val.language]);
		if(rs.isValidRow()) {
			this.db.execute('update wirings set working=? where name=? and language=?', [val.working, val.name, val.language]);
		}
		else {
			this.db.execute('insert into wirings values (?, ?, ?)', [val.name, val.working, val.language]);
		}
		callbacks.success.call(callbacks.scope, "ok");
	},
	
	deleteWiring: function(val, callbacks) {
		this.db.execute('delete from wirings where name=? and language=?', [val.name, val.language]);
		callbacks.success.call(callbacks.scope, "ok");
	},
	
	listWirings: function(val, callbacks) {
		var rs = this.db.execute('select * from wirings where language=?', [val.language]);
		var results = [];
		while (rs.isValidRow()) {
			results.push({
				name: rs.field(0),
				working: rs.field(1),
				language: rs.field(2)
			});
		  rs.next();
		}
		rs.close();
		callbacks.success.call(callbacks.scope, results);
	}
	
};
