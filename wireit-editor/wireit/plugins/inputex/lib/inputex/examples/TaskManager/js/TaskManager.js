
// Needed for inputEx
inputEx.spacerUrl = "../images/space.gif";

/**
 * Main TaskManager object
 */
var TaskManager = {
   
   // Map of YAHOO.widget.TextNode instances in the TreeView instance.
   oTextNodeMap: {},
   
   // Remember the last clicked task
   oEditingTaskNode: null,
   
   // The YAHOO.widget.TextNode instance whose "contextmenu" 
   // DOM event triggered the display of the  ContextMenu instance.
   oCurrentTextNode: null,
   
   // Treeview instance
   oTreeView: null,
   
   // Task Details Form
   oTaskDetailsForm: null,
   
   /**
    * Init the taskManager
    */
   init: function() {
      this.buildTree();
      this.initContextMenu();
      this.buildForm();
      this.initEvents();
      this.queryData();
   },
   
   /**
    * Create the Task Details Form
    */
   buildForm: function() {
      this.oTaskDetailsForm = new inputEx.Group({parentEl: 'taskInformation', fields: [
            {label: 'Description', name: 'description'},
      		{type: 'date', label: 'Due date', name: 'duedate'},
            {label: 'Tags', name: 'tags'},
      		{type:'text', label: 'Comments', name:'comments'}
      ] });
   },
   
   /**
    * Init the events
    */
   initEvents: function() {
      // Save button
      YAHOO.util.Event.addListener('saveTreeButton', 'click', this.onSaveClick, this, true);
      
      // "Add Root Node" button
      YAHOO.util.Event.addListener('addRootNode', 'click', function(e) {
         YAHOO.util.Event.stopEvent(e);
         this.addNode(this.oTreeView.getRoot());
      }, this, true);
      
      // Updated event sent by the form
      this.oTaskDetailsForm.updatedEvt.subscribe(this.onTaskDetailsUpdated, this, true);
   },
   
   /**
    * Update the task details value
    */
   onTaskDetailsUpdated: function(e) {
      this.oEditingTaskNode._taskDetails = this.oTaskDetailsForm.getValue();
      var sLabel = this.oEditingTaskNode._taskDetails.description;
      if (sLabel && sLabel.length > 0) {
            this.oEditingTaskNode.getLabelEl().innerHTML = sLabel;
            this.oEditingTaskNode.label = sLabel;
       }
   },
   
   /**
    * Save button click
    */ 
   onSaveClick: function() {
      var value = [];
      var rootNode = this.oTreeView.getRoot();
      
      for(var i = 0 ; i < rootNode.children.length ; i++) {
         var childNode = rootNode.children[i];
         value.push( childNode.toJsObject() );
      }
      var json = YAHOO.lang.JSON.stringify(value);
      
      YAHOO.util.Dom.get('saveStatus').innerHTML = "saving...";

		alert("send the following json to your server :"+json);

		// Exemple of a real world application :
      /*YAHOO.util.Connect.asyncRequest('POST', 'store.php', { 
         success: function(o) {
            
         }, 
         failure: function(o) {
            YAHOO.util.Dom.get('saveStatus').innerHTML = "error !";
         }
      }, "data="+json);*/

		var d = new Date();
      YAHOO.util.Dom.get('saveStatus').innerHTML = "saved at "+d.getHours()+":"+d.getMinutes()+":"+d.getSeconds();
   },
   
   /**
    * Ajax request to retreive the data
    */
   queryData: function() {
      YAHOO.util.Connect.asyncRequest('GET', 'store.json', { 
         success: function(o) {
            var childNodes = YAHOO.lang.JSON.parse(o.responseText);
            this.populateTree(childNodes);
         }, 
         failure: function(o) {
            //console.log(o.responseText);
         },
         scope: this
      }, null);
   },
   
   /**
    * Populate the tree with the tasks 
    */
   populateTree: function(childNodes) {
      
      // Function that render the branch
      var buildBranch = function(nodeInfos, parentNode) {
         var oTextNode = new YAHOO.widget.TaskNode(nodeInfos.label, parentNode, false, nodeInfos.checked);   
         this.oTextNodeMap[oTextNode.labelElId] = oTextNode;
         oTextNode._taskDetails = nodeInfos._taskDetails;
         for(var i = 0 ; i < nodeInfos.children.length ; i++) {
            var n = nodeInfos.children[i];
            buildBranch.call(this, n, oTextNode);
         }
      };
      for(var i = 0 ; i < childNodes.length ; i++) {
         var nodeInfos = childNodes[i];
         buildBranch.call(this, nodeInfos, this.oTreeView.getRoot() );
      }
      this.oTreeView.draw();
   },
   
   /**
    * Render the treeview
    */
   buildTree: function() {
      // Create a TreeView instance
      this.oTreeView = new YAHOO.widget.TreeView("taskTreeView");
   },
   
   /**
    * Add a "Unamed" node to the parentEl and focus on the description field
    */
   addNode: function(parentNode) {
      
      var oChildNode = new YAHOO.widget.TaskNode("Unamed", parentNode, false);
      this.oTextNodeMap[oChildNode.labelElId] = oChildNode;
      
      parentNode.refresh();
      parentNode.expand();
       
      this.setEditingTaskNode(oChildNode);
      this.oTaskDetailsForm.inputsNames["description"].el.focus();
      this.oTaskDetailsForm.inputsNames["description"].el.setSelectionRange(0,6);
   },
   
   /**
    * Create the context menu
    */
   initContextMenu: function() {

      var that = this;
      var oContextMenu = new YAHOO.widget.ContextMenu("mytreecontextmenu", {
                                                      trigger: "taskTreeView",
                                                      lazyload: true, 
                                                      itemdata: [
                                                          { text: "Add Subtask", onclick: { fn: function() { that.addNode(that.oCurrentTextNode); } } },
                                                          { text: "Delete Task", onclick: { fn: function() {
                                                             delete that.oTextNodeMap[that.oCurrentTextNode.labelElId];
                                                              that.oTreeView.removeNode(that.oCurrentTextNode);
                                                              that.oTreeView.draw();
                                                          } } }
                                                      ] });

      // Subscribe to the "contextmenu" event for the element(s) specified as the "trigger" for the ContextMenu instance.
      oContextMenu.subscribe("triggerContextMenu", this.onTriggerContextMenu);

   },
   
   /**
    * Get the TaskNode instance that that triggered the display of the ContextMenu instance.
    * and keep it in TaskManager.oCurrentTextNode
    */
   onTriggerContextMenu: function(p_oEvent) {
      
       function getTextNodeFromEventTarget(p_oTarget) {
           if (p_oTarget.tagName.toUpperCase() == "A" && YAHOO.util.Dom.hasClass(p_oTarget, "ygtvlabel") ) {
               return TaskManager.oTextNodeMap[p_oTarget.id];
           }
           else {
               if (p_oTarget.parentNode && p_oTarget.parentNode.nodeType == 1) {
                   return getTextNodeFromEventTarget(p_oTarget.parentNode);
               }
           }
       }

       // 
       var oTextNode = getTextNodeFromEventTarget(this.contextEventTarget);
       if (oTextNode) {
           TaskManager.oCurrentTextNode = oTextNode;
       }
       else {
           // Cancel the display of the ContextMenu instance.
           this.cancel();
       }
   },
   
   /**
    * Set the CSS class for the newly selected class and update the form
    */
   setEditingTaskNode: function(node) {
      
      // Update CSS class
      if(this.oEditingTaskNode) {
         YAHOO.util.Dom.removeClass( this.oEditingTaskNode.getLabelEl(), "selectedTask" );
      }
      YAHOO.util.Dom.addClass( node.getLabelEl(), "selectedTask" );
      
      // Keep a reference to the last clicked node
      this.oEditingTaskNode = node;
      
      // Set the form values
      this.oTaskDetailsForm.setValue(this.oEditingTaskNode._taskDetails || {
         description: this.oEditingTaskNode.label,
         duedate: "",
         tags: "",
         comments: ""
      });
      
   }
   
};

// Init
YAHOO.util.Event.onDOMReady(TaskManager.init, TaskManager, true);
