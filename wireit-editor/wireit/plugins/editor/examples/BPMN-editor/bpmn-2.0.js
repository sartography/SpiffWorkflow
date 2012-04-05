var bpmnLanguage = {
	
	// Set a unique name for the language
	languageName: "bpmn2.0",

	// inputEx fields for pipes properties
	propertiesFields: [
		// default fields (the "name" field is required by the WiringEditor):
		{"type": "string", "name": "name", label: "Title", typeInvite: "Enter a title" },
		{"type": "text", "name": "description", label: "Description", cols: 30 }
	],
	
	// List of node types definition
	modules: [
	
	
		/*
			ACTIVITIES
		*/
		{
			"name": "Task",
			"category": "activity",
			"container": {
      		"xtype":"WireIt.FormContainer", 
      		"className": "WireIt-Container WireIt-ImageContainer BPMN-Task",
         	"icon": "icons/activity/task.png",
      		"image": "icons/activity/task.png",
      		"terminals": [
      				{"direction": [-1,0], "offsetPosition": {"left": -15, "top": 35 }, "name": "in"},
						{"direction": [1,0], "offsetPosition": {"right": -15, "top": 35 }, "name": "out"}
      		],
				resizable: false,
				"fields": [ 
					{type: 'inplaceedit', name: 'content',	editorField: {type: 'text'} }
				]
      	}
      },

		{
			"name": "Collapsed Subprocess",
			"category": "activity",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/activity/subprocess.png",
      		"image": "icons/activity/subprocess.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Expanded Subprocess",
			"category": "activity",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/activity/expanded.subprocess.png",
      		"image": "icons/activity/expanded.subprocess.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Collapsed Event-Subprocess",
			"category": "activity",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/activity/event.subprocess.collapsed.png",
      		"image": "icons/activity/event.subprocess.collapsed.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Event-Subprocess",
			"category": "activity",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/activity/event.subprocess.png",
      		"image": "icons/activity/event.subprocess.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		/*
			GATEWAYS
		*/
		
		{
			"name": "Data-based Exclusive (XOR) Gateway",
			"category": "gateway",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/gateway/exclusive.databased.png",
      		"image": "images/gateway/exclusive.png",
      		"terminals": [
      				{"direction": [-1,0], "offsetPosition": {"left": -20, "top": 7 }, "name": "in"},
      				{"direction": [1,0], "offsetPosition": {"right": -20, "top": 7 }, "name": "out"}
      		]
      	}
      },

		{
			"name": "Event-based Gateway",
			"category": "gateway",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/gateway/eventbased.png",
      		"image": "icons/gateway/eventbased.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Parallel Gateway",
			"category": "gateway",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/gateway/parallel.png",
      		"image": "icons/gateway/parallel.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Inclusive Gateway",
			"category": "gateway",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/gateway/inclusive.png",
      		"image": "icons/gateway/inclusive.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Complex Gateway",
			"category": "gateway",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/gateway/complex.png",
      		"image": "icons/gateway/complex.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },
	
	
		/*
			Swimlanes
		*/
		
		{
			"name": "Pool",
			"category": "swimlane",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/swimlane/pool.png",
      		"image": "icons/swimlane/pool.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Collapsed Pool",
			"category": "swimlane",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/swimlane/lane.png",
      		"image": "icons/swimlane/lane.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Lane",
			"category": "swimlane",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/swimlane/lane.png",
      		"image": "icons/swimlane/lane.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		/*
			Artifacts
		*/
		
		{
			"name": "Group",
			"category": "artifact",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/artifact/group.png",
      		"image": "icons/artifact/group.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Text Annotation",
			"category": "artifact",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/artifact/text.annotation.png",
      		"image": "icons/artifact/text.annotation.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },
		
		/*
			Data Objects
		*/
		
		{
			"name": "Data Object",
			"category": "dataobject",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/dataobject/data.object.png",
      		"image": "icons/dataobject/data.object.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "IT System",
			"category": "dataobject",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/dataobject/it.system.png",
      		"image": "icons/dataobject/it.system.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Data Store",
			"category": "dataobject",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/dataobject/data.store.png",
      		"image": "icons/dataobject/data.store.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Message",
			"category": "dataobject",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/dataobject/message.png",
      		"image": "icons/dataobject/message.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		/*
			START EVENTS
		*/
		
		{
			"name": "Start Event",
			"category": "startevent",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/startevent/none.png",
      		"image": "icons/startevent/none.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Start Message Event",
			"category": "startevent",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/startevent/message.png",
      		"image": "icons/startevent/message.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Start Timer Event",
			"category": "startevent",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/startevent/timer.png",
      		"image": "icons/startevent/timer.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Start Conditional Event",
			"category": "startevent",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/startevent/conditional.png",
      		"image": "icons/startevent/conditional.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Start Error Event",
			"category": "startevent",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/startevent/error.png",
      		"image": "icons/startevent/error.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Start Compensation Event",
			"category": "startevent",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/startevent/compensation.png",
      		"image": "icons/startevent/compensation.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Start Signal Event",
			"category": "startevent",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/startevent/signal.png",
      		"image": "icons/startevent/signal.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Start Multiple Event",
			"category": "startevent",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/startevent/multiple.png",
      		"image": "icons/startevent/multiple.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Start Parallel Multiple Event",
			"category": "startevent",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/startevent/multiple.parallel.png",
      		"image": "icons/startevent/multiple.parallel.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },
		
		{
			"name": "Start Escalation Event",
			"category": "startevent",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/startevent/escalation.png",
      		"image": "icons/startevent/escalation.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		/*
		  Catching
		*/

		{
			"name": "Intermediate Message Event",
			"category": "catching",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/catching/message.png",
      		"image": "icons/catching/message.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Intermediate Timer Event",
			"category": "catching",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/catching/timer.png",
      		"image": "icons/catching/timer.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },
		
		{
			"name": "Intermediate Conditional Event",
			"category": "catching",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/catching/conditional.png",
      		"image": "icons/catching/conditional.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Intermediate Link Event",
			"category": "catching",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/catching/link.png",
      		"image": "icons/catching/link.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Intermediate Error Event",
			"category": "catching",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/catching/error.png",
      		"image": "icons/catching/error.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Intermediate Cancel Event",
			"category": "catching",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/catching/cancel.png",
      		"image": "icons/catching/cancel.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },
		
		{
			"name": "Intermediate Compensation Event",
			"category": "catching",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/catching/compensation.png",
      		"image": "icons/catching/compensation.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },
		
		{
			"name": "Intermediate Signal Event",
			"category": "catching",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/catching/signal.png",
      		"image": "icons/catching/signal.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },
		
		{
			"name": "Intermediate Multiple Event",
			"category": "catching",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/catching/multiple.png",
      		"image": "icons/catching/multiple.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },
		{
			"name": "Intermediate Parallel Multiple Event",
			"category": "catching",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/catching/multiple.parallel.png",
      		"image": "icons/catching/multiple.parallel.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Intermediate Escalation Event",
			"category": "catching",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/catching/escalation.png",
      		"image": "icons/catching/escalation.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },
		
		/*
		  Throwing
		*/
		
		{
			"name": "Intermediate Event",
			"category": "throwing",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/throwing/none.png",
      		"image": "icons/throwing/none.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Intermediate Message Event",
			"category": "throwing",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/throwing/message.png",
      		"image": "icons/throwing/message.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Intermediate Link Event",
			"category": "throwing",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/throwing/link.png",
      		"image": "icons/throwing/link.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Intermediate Compensation Event",
			"category": "throwing",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/throwing/compensation.png",
      		"image": "icons/throwing/compensation.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Intermediate Signal Event",
			"category": "throwing",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/throwing/signal.png",
      		"image": "icons/throwing/signal.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Intermediate Multiple Event",
			"category": "throwing",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/throwing/multiple.png",
      		"image": "icons/throwing/multiple.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Intermediate Escalation",
			"category": "throwing",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/throwing/escalation.png",
      		"image": "icons/throwing/escalation.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		/*
			END EVENTS
		*/

		{
			"name": "End Event",
			"category": "endevent",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/endevent/none.png",
      		"image": "icons/endevent/none.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "End Message Event",
			"category": "endevent",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/endevent/message.png",
      		"image": "icons/endevent/message.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "End Error Event",
			"category": "endevent",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/endevent/error.png",
      		"image": "icons/endevent/error.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Cancel End Event",
			"category": "endevent",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/endevent/cancel.png",
      		"image": "icons/endevent/cancel.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "End Compensation Event",
			"category": "endevent",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/endevent/compensation.png",
      		"image": "icons/endevent/compensation.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "End Signal Event",
			"category": "endevent",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/endevent/signal.png",
      		"image": "icons/endevent/signal.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "End Multiple Event",
			"category": "endevent",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/endevent/multiple.png",
      		"image": "icons/endevent/multiple.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Terminate End Event",
			"category": "endevent",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/endevent/terminate.png",
      		"image": "icons/endevent/terminate.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "End Escalation Event",
			"category": "endevent",
			"container": {
      		"xtype":"WireIt.ImageContainer", 
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/endevent/escalation.png",
      		"image": "icons/endevent/escalation.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },
		
		/*
			Connecting Objects
		*/
		
		{
			"name": "Sequence Flow",
			"category": "connector",
			"container": {
      		"xtype":"WireIt.ImageContainer",  // TODO: WireIt.Wire
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/connector/sequenceflow.png",
      		"image": "icons/connector/sequenceflow.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Message Flow",
			"category": "connector",
			"container": {
      		"xtype":"WireIt.ImageContainer",  // TODO: WireIt.Wire
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/connector/messageflow.png",
      		"image": "icons/connector/messageflow.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Association (undirected)",
			"category": "connector",
			"container": {
      		"xtype":"WireIt.ImageContainer",  // TODO: WireIt.Wire
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/connector/association.undirected.png",
      		"image": "icons/connector/association.directional.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Association (unidirectional)",
			"category": "connector",
			"container": {
      		"xtype":"WireIt.ImageContainer",  // TODO: WireIt.Wire
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/connector/association.unidirectional.png",
      		"image": "icons/connector/association.unidirectional.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

		{
			"name": "Association (bidirectional)",
			"category": "connector",
			"container": {
      		"xtype":"WireIt.ImageContainer",  // TODO: WireIt.Wire
      		//"className": "WireIt-Container WireIt-ImageContainer",
         	"icon": "icons/connector/association.bidirectional.png",
      		"image": "icons/connector/association.bidirectional.png",
      		"terminals": [
      				{"direction": [-1,-1], "offsetPosition": {"left": -10, "top": -10 }, "name": "tl"}
      		]
      	}
      },

	
	   /*{
	      "name": "FormContainer",
			"category": "form",
	      "container": {
	   		"xtype": "WireIt.FormContainer",
	   		"title": "WireIt.FormContainer demo",    
	   		"icon": "../../res/icons/application_edit.png",

	   		"collapsible": true,
	   		"fields": [ 
	   			{"type": "select", "label": "Title", "name": "title", "selectValues": ["Mr","Mrs","Mme"] },
	   			{"label": "Firstname", "name": "firstname", "required": true }, 
	   			{"label": "Lastname", "name": "lastname", "value":"Dupont"}, 
	   			{"type":"email", "label": "Email", "name": "email", "required": true, "wirable": true }, 
	   			{"type":"boolean", "label": "Happy to be there ?", "name": "happy" }, 
	   			{"type":"url", "label": "Website", "name":"website", "size": 25 } 
	   		],
	   		"legend": "Tell us about yourself..."
	   	}
	   },
	
		{
	      "name": "comment",
	
	      "container": {
	         "xtype": "WireIt.FormContainer",
				"icon": "../../res/icons/comment.png",
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
	      		"icon": "../../res/icons/arrow_join.png",
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
	            	"icon": "../../res/icons/color_wheel.png",
	         		"image": "../images/bubble.png",
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
	   				"icon": "../../res/icons/application_edit.png",
	   				"xtype": "WireIt.FormContainer",
	   				"outputTerminals": [],
	   				"propertiesForm": [],
	   				"fields": [ 
	   					{"type": "select", "label": "Title", "name": "title", "selectValues": ["Mr","Mrs","Mme"] } },
	   					{"label": "Firstname", "name": "firstname", "required": true }, 
	   					{"label": "Lastname", "name": "lastname", "value":"Dupont"}, 
	   					{"type":"email", "label": "Email", "name": "email", "required": true }, 
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
	         		"icon": "../../res/icons/comments.png",

	         		"fields": [ 

	         		   {"type": "inplaceedit", 
										"name": "post",
	         		      "editorField":{"type":"text" },  
	         		      "animColors":{"from":"#FFFF99" , "to":"#DDDDFF"}
	         		   },

	         			{"type": "list", 
	         			   "label": "Comments", "name": "comments", "wirable": false,
	         			   "elementType": {"type":"string","wirable": false }
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
		      		"icon": "../../res/icons/arrow_right.png",
						"inputs": ["text1", "text2", "option1"],
						"outputs": ["result", "error"]
		      	}
		      }*/
				
			],
			
			layoutOptions: {
			 	units: [
			   	{ position: 'top', height: 57, body: 'top'},
			      { position: 'left', width: 290, resize: true, body: 'left', gutter: '5px', collapse: true, 
			        collapseSize: 25, header: 'BPMN Modules', scroll: true, animate: true },
			      { position: 'center', body: 'center', gutter: '5px' },
			      { position: 'right', width: 320, resize: true, body: 'right', gutter: '5px', collapse: true, 
			        collapseSize: 25, /*header: 'Properties', scroll: true,*/ animate: true }
			   ]
			}
};


// InputEx needs a correct path to this image
inputEx.spacerUrl = "/inputex/trunk/images/space.gif";



BPMNEditor = function(options) {
   BPMNEditor.superclass.constructor.call(this, options);
};

YAHOO.lang.extend(BPMNEditor, WireIt.WiringEditor, {
   

	onLoadSuccess: function(wirings) {
			this.pipes = wirings;
			this.pipesByName = {};

			this.renderLoadPanel();
	    	this.updateLoadPanelList();

			if(!this.afterFirstRun) {
				var p = window.location.search.substr(1).split('&');
				var oP = {};
				for(var i = 0 ; i < p.length ; i++) {
					var v = p[i].split('=');
					oP[v[0]]=window.decodeURIComponent(v[1]);
				}
				this.afterFirstRun = true;
				if(oP.autoload) {
					this.loadPipe(oP.autoload);
					return;
				}
			}

	    //this.loadPanel.show();
	}

});

YAHOO.util.Event.onDOMReady( function() {
	
	var editor = new BPMNEditor(bpmnLanguage); 
	
	// Open the infos panel
	//editor.accordionView.openPanel(2);
	
});


