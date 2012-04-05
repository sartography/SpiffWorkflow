/* base-schema.js
 *
 * http://groups.google.com/group/json-schema/web/json-schema-proposal---second-draft
 * 
*/


/* a list of schemas */

var base_schema_map = {
    "address": {
	    id:'address',
	    type:'object',
	    properties:{
    		'address1':{
    			'type':'string',
    			'title':'Address'
    		},
    		'address2':{
    			'type':'string',
    			'optional':true,
    			'title':' '
    		},
    		'city':{
    			'type':'string',
    			'title':'City'
    		},
    		'state':{
    			'type':'string',
    			'minLength':2,
    			'maxLength':2,
    			'pattern':/^[A-Za-z][A-Za-z]$/,
    			'title':'State'
    			
    		},
    		'postal_code':{
    			'type':'string',
    			'pattern':/(^\d{5}-\d{4}$)|(^\d{5}$)/,
    			'title':'Zip'
    		}
   	}
    },
    "information-source": {
	    id:'information-source',
	    type:'object',
	    properties:{
    		'name':{
    			'type':'string',
    			'title':'Organization'
    		},
    		'contact':{
    			'type':'string',
    			'optional':true,
    			'title':'Contact Name'
    		},
    		'physical_address':{
    			'$ref':'address',
    			'optional':true,
    			'title':'Physical Address'
    		},
    		'postal_address':{
    			'$ref':'address',
    			'title':'Postal Address'
    		},
    		'telephone':{
    			'type':'string',
    			'pattern':/^\d{3}-\d{3}-\d{4}$/,
    			'title':'Telephone'
    		},
    		'email':{
    			'type':'string',
    			'format':'email',
    			'optional':true,
    			'title':'Email'
    		},
    		'url':{
        		'type':'string',
        		'format':'url',
        		'optional':true,
    			'title':'Website'        		
    		}
    	}
    },
	'community': {
		'id':'community',
		'type':'object',
		'properties':{
			'community_id':{
				'type':'number',
				'title':'Community ID'
			},
			'display_name':{
				'type':'string',
				'title':'Community Name'
			},
			'short_description':{
				'type':'string',
				'format':'text',
				'title':'Short Description',
				'_inputex':{
					'rows':5,
					'cols':50
				}
			},
			'long_description':{
				'type':'string',
				'format':'html',
				'title':'Long Description',
			    "_inputex":{
				    "opts":{
				    	'width':'500',
				    	'height':'200'
			    	}
				}
			},
		    "information_sources": {
			   "title":"Information Sources",
				"type":"array",
			    "items":{
					"$ref":"information-source"
			    },
			    "_inputex":{
				    "useButtons":false,
				    "sortable":true
			    }
			}
		}
    }
};
