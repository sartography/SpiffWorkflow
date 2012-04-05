var SpiffWorkflowLanguage = {
    languageName: "SpiffWorkflow",

    // Editor layout.
    layoutOptions: {
        units: [
            {
                position: 'top',
                height: 27,
                body: 'top'
            },
            {
                position: 'left',
                width: 290,
                resize: true,
                body: 'left',
                gutter: '5px',
                collapse: true,
                collapseSize: 25,
                header: 'Workflow Components',
                scroll: true,
                animate: true
            },
            {
                position: 'center',
                body: 'center',
                gutter: '5px'
            },
            {
                position: 'right',
                width: 320,
                resize: true,
                body: 'right',
                gutter: '5px',
                collapse: true,
                collapseSize: 25,
                header: 'Tools',
                //scroll: true,
            }
        ]
    },

    // Workflow properties.
    propertiesFields: [
        {
            "type": "string",
            "name": "name",
            label: "Title:",
            typeInvite: "Enter a workflow title"
        },
        {
            "type": "text",
            "name": "description",
            label: "Description:",
            cols: 50
        }
    ],

    // Workflow components.
    modules: [
        /* Windows */
        {
            "name": "Window",
            "category": "task",
            "container": {
                "xtype": "WireIt.MyFormContainer",
                "title": "Workflow Task",
                "icon": "icons/application_edit.png",
                "collapsible": true,
                "terminals": [
                    {
                        "direction": [0,-1],
                        "offsetPosition": {"top": 0, "left": 150},
                        "name": "in",
                        "ddConfig": {
                            "type": "input",
                            "allowedTypes": ["output"]
                        }
                    },
                    {
                        "direction": [0,1],
                        "offsetPosition": {"bottom": -14, "left": 150},
                        "name": "out",
                        "ddConfig": {
                            "type": "output",
                            "allowedTypes": ["input"]
                        }
                    }
                ],
                "fields": [
                    {
                        "type": "select",
                        "label": "Title:",
                        "name": "title",
                        "selectValues": ["Mr","Mrs","Mme"]
                    },
                    {
                        "label": "Firstname:",
                        "name": "firstname",
                        "required": true
                    },
                    {
                        "label": "Lastname:",
                        "name": "lastname",
                        "value": "Dupont"
                    }
                ],
            }
        },


        /* Flow Control */
        {
            "name": "Exclusive Choice",
            "category": "flow",
            "container": {
                "xtype": "WireIt.ImageContainer",
                "icon": "icons/exclusive_choice.png",
                "image": "images/exclusive_choice.png",
                "terminals": [
                    {
                        "direction": [0,-1],
                        "offsetPosition": {"left": 7, "top": -20 },
                        "name": "in",
                        "ddConfig": {
                            "type": "input",
                            "allowedTypes": ["output"]
                        }
                    },
                    {
                        "direction": [-1,0],
                        "offsetPosition": {"left": -20, "top": 7 },
                        "name": "out1",
                        "ddConfig": {
                            "type": "output",
                            "allowedTypes": ["input"]
                        }
                    },
                    {
                        "direction": [1,0],
                        "offsetPosition": {"right": -20, "top": 7 },
                        "name": "out2",
                        "ddConfig": {
                            "type": "output",
                            "allowedTypes": ["input"]
                        }
                    }
                ]
            }
        }
    ]
};

SpiffWorkflowEditor = function(options) {
   SpiffWorkflowEditor.superclass.constructor.call(this, options);
};

YAHOO.lang.extend(SpiffWorkflowEditor, WireIt.WiringEditor, {
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
    }
});

WireIt.MyFormContainer = function(options, layer) {
    WireIt.MyFormContainer.superclass.constructor.call(this, options, layer);
};

YAHOO.lang.extend(WireIt.MyFormContainer, WireIt.FormContainer, {
    onMouseDown: function() {
        new inputEx.StringField({
            name: "mystringfield",
            label: "My String:",
            value: 'Test',
            parentEl: 'propertiesForm'
        });

        SpiffWorkflowLanguage.propertiesFields.push(
            {
                "type": "text",
                "name": "descr",
                label: "Description 2:",
                cols: 50
            }
        );
    }
});
