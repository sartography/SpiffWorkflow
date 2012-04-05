var demoLanguage = {
	
	// Set a unique name for the language
	languageName: "meltingpotDemo",

	// inputEx fields for pipes properties
	propertiesFields: [
		// default fields (the "name" field is required by the WiringEditor):
		{"type": "string", "name": "name", label: "Title", typeInvite: "Enter a title" },
		{"type": "text", "name": "description", label: "Description", cols: 30},
		
		// Additional fields
		{"type": "boolean", "name": "isTest", value: true, label: "Test" },
		{"type": "select", "name": "category", label: "Category", selectValues: ["Demo", "Test", "Other"] }
	],
	
	// List of node types definition
	modules: [
	
	   {
	      "name": "FormContainer",
			"category": "form",
	      "container": {
	   		"xtype": "WireIt.FormContainer",
	   		"title": "WireIt.FormContainer demo",    
	   		"icon": "../../assets/application_edit.png",

	   		"collapsible": true,
	   		"fields": [ 
	   			{"type": "select", "label": "Title", "name": "title", "selectValues": ["Mr","Mrs","Mme"] },
	   			{"type": "string", "label": "Firstname", "name": "firstname", "required": true } , 
	   			{"type": "string", "label": "Lastname", "name": "lastname", "value":"Dupont"}, 
	   			{"type":"email", "label": "Email", "name": "email", "required": true, "wirable": true }, 
	   			{"type":"boolean", "label": "Happy to be there ?", "name": "happy" }, 
	   			{"type":"url", "label": "Website", "name":"website", "size": 25}
	   		],
	   		"legend": "Tell us about yourself..."
	   	}
	   },
	
		{
	      "name": "comment",
	
	      "container": {
	         "xtype": "WireIt.FormContainer",
				"icon": "../../assets/comment.png",
	   		"title": "Comment",
	   		"fields": [
	            {"type": "text", "label": "", "name": "comment", "wirable": false }
	         ]
	      },
	      "value": {
	         "input": {
	            "type":"url"
	         }
	      }
	   },

	      {
	         "name": "AND gate",
				"category": "images",
	         "container": {
	      		"xtype":"WireIt.ImageContainer", 
	      		"image": "../logicGates/images/gate_and.png",
	      		"icon": "../../assets/arrow_join.png",
	      		"terminals": [
	      			{"name": "_INPUT1", "direction": [-1,0], "offsetPosition": {"left": -3, "top": 2 }},
	      			{"name": "_INPUT2", "direction": [-1,0], "offsetPosition": {"left": -3, "top": 37 }},
	      			{"name": "_OUTPUT", "direction": [1,0], "offsetPosition": {"left": 103, "top": 20 }}
	      		]
	      	}
	      },


				{
					"name": "Bubble",
					"category": "images",
					"container": {
	         		"xtype":"WireIt.ImageContainer", 
	         		"className": "WireIt-Container WireIt-ImageContainer Bubble",
	            	"icon": "../../assets/color_wheel.png",
	         		"image": "../../../../examples/bubble.png",
	         		"terminals": [
	         				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"},
	         				{"direction": [1,-1], "offsetPosition": {"left": 25, "top": -10 }, "name": "tr"},
	         				{"direction": [-1,1], "offsetPosition": {"left": -10, "top": 25 }, "name": "bl"},
	         				{"direction": [1,1], "offsetPosition": {"left": 25, "top": 25 }, "name": "br"}
	         		]
	         	}
		      },

				{
					"name": "Other form module",
					"category": "form",
					"container": {
	   				"icon": "../../assets/application_edit.png",
	   				"xtype": "WireIt.FormContainer",
	   				"outputTerminals": [],
	   				"propertiesForm": [],
	   				"fields": [ 
	   					{"type": "select", "label": "Title", "name": "title", "selectValues": ["Mr","Mrs","Mme"] },
	   					{"label": "Firstname", "name": "firstname", "required": true }, 
	   					{"label": "Lastname", "name": "lastname", "value":"Dupont"}, 
	   					{"type":"email", "label": "Email", "name": "email", "required": true}, 
	   					{"type":"boolean", "label": "Happy to be there ?", "name": "happy"}, 
	   					{"type":"url", "label": "Website", "name":"website", "size": 25} 
	   				]
					}
				},

				{
	            "name": "PostContainer",
					"category": "form",
	            "container": {
	         		"xtype": "WireIt.FormContainer",
	         		"title": "Post",    
	         		"icon": "../../assets/comments.png",

	         		"fields": [ 

	         		   {"type": "inplaceedit", 
										"name": "post",
	         		      "editorField":{"type":"text"},  
	         		      "animColors":{"from":"#FFFF99" , "to":"#DDDDFF"}
	         		   },

	         			{"type": "list",
	         			   "label": "Comments", "name": "comments", "wirable": false,
	         			   "elementType": {"type":"string", "wirable": false }
	         			}

	         		],

	         		   	"terminals": [
	               			{"name": "SOURCES", "direction": [0,-1], "offsetPosition": {"left": 100, "top": -15 }},
	               			{"name": "FOLLOWUPS", "direction": [0,1], "offsetPosition": {"left": 100, "bottom": -15}}
	               			]
	         	}
	         },
	
	
				{
		         "name": "InOut test",
		         "container": {
		      		"xtype":"WireIt.InOutContainer", 
		      		"icon": "../../assets/arrow_right.png",
						"inputs": ["text1", "text2", "option1"],
						"outputs": ["result", "error"]
		      	}
		      }
				
			]

};