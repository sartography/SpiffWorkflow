// InputEx French localization
(function() {
   
   var msgs = inputEx.messages;

   msgs.required = "Ce champ est obligatoire";
   msgs.invalid = "Ce champ n'est pas valide";
   msgs.valid = "Ce champ est valide";
   
   msgs.invalidEmail = "Email non valide; ex: michel.dupont@fai.fr";
   msgs.didYouMeant = "Voulez-vous dire : ";
   msgs.selectColor = "S&eacute;lectionnez une couleur :";
   msgs.invalidPassword = ["Le mot de passe doit contenir au moins "," caract&egrave;res (lettres ou chiffres)"];
   msgs.invalidPasswordConfirmation = "Les mots de passe entrés ne sont pas identiques !";
   msgs.passwordStrength = "Solidité du mot de passe";
   msgs.capslockWarning = "Attention: touche majuscule activée";
   msgs.invalidDate = "Date non valide; ex: 25/01/2007";
   msgs.defaultDateFormat = "d/m/Y";
   msgs.shortMonths = ["Jan", "Fév", "Mars", "Avril", "Mai", "Juin", "Juil", "Août", "Sept", "Oct", "Nov", "Déc"];
   msgs.months = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"];
   msgs.weekdays1char =  ["D", "L", "M", "M", "J", "V", "S"];
   msgs.shortWeekdays = ["Di","Lu","Ma","Me","Je","Ve","Sa"];
   msgs.selectMonth = "- Choisissez -";
   msgs.dayTypeInvite = "Jour";
   msgs.monthTypeInvite = "Mois";
   msgs.yearTypeInvite = "Année";
   msgs.cancelEditor = "annuler";
   msgs.okEditor = "Ok";
   msgs.defautCalendarOpts = {
      navigator: {
               strings : {
                   month: "Choisissez un mois",
                   year: "Entrez une année",
                   submit: "Ok",
                   cancel: "Annuler",
                   invalidYear: "Année non valide"
               }
      },
      start_weekday: 1 // la semaine commence un lundi
   };
   msgs.stringTooShort = ["Ce champ doit contenir au moins "," caract&egrave;res (lettres ou chiffres)"];
   msgs.stringTooLong = ["Ce champ doit contenir au plus "," caract&egrave;res (lettres ou chiffres)"];
   msgs.ajaxWait = "Envoi en cours...";
   msgs.menuTypeInvite = "Cliquez ici pour choisir";
   
   // List
   msgs.listAddLink = "Ajouter";
   msgs.listRemoveLink = "Supprimer";
   
   // Datatable
   msgs.saveText = "Sauver";
   msgs.cancelText = "Annuler";
   msgs.modifyText = "modifier";
   msgs.deleteText = "supprimer";
   msgs.insertItemText = "Ajouter";
   msgs.confirmDeletion = "Êtes-vous sûr ?";
	msgs.addButtonText = "Ajouter";
	msgs.loadingText = "Patientez...";
	msgs.emptyDataText = "Aucune donnée.";
	msgs.errorDataText = "Erreur de données.";
	
	msgs.tableOptions = "Options des colonnes";
	msgs.showColumnButton = "Afficher";
	msgs.hideColumnButton = "Masquer";
	msgs.columnDialogTitle = "Choisissez les colonnes à afficher";
	msgs.columnDialogCloseButton = "Fermer";
   
   // TimeInterval
   msgs.timeUnits = {
      SECOND: "secondes",
      MINUTE: "minutes",
      HOUR: "heures",
      DAY: "jours",
      MONTH: "mois",
      YEAR: "ans"
   };
   
   // for YUI loader 
   inputEx.lang_fr = true;
   
})();