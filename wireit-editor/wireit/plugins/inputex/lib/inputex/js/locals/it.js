// InputEx Italian localization (Big Thanks to alexodus !)
(function() {

   var msgs = inputEx.messages;

   msgs.required = "Questo campo è obbligatorio";
   msgs.invalid = "Questo campo non è stato validato";
   msgs.valid = "Questo campo è stato validato";
   msgs.invalidEmail = "Email non valida; es: antonio.rossi@fai.it";
   msgs.selectColor = "Seleziona un colore:";
   msgs.invalidPassword = ["La password deve contenere almeno ","numeri o lettere"];
   msgs.invalidPasswordConfirmation = "le password sono differenti !";
   msgs.capslockWarning = "Attenzione: tasto maiuscole attive";
   msgs.invalidDate = "Data non valida; es: 25/01/2007";
   msgs.defaultDateFormat = "d/m/Y";
   msgs.shortMonths = ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu","Lug", "Ago", "Set", "Ott", "Nov", "Dic"];
   msgs.months = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio","Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre","Dicembre"];
   msgs.weekdays1char =  ["D", "L", "M", "M", "G", "V", "S"];
   msgs.shortWeekdays = ["Do","Lu","Ma","Me","Gi","Ve","Sa"];
   msgs.selectMonth = "- Seleziona Mese -";
   msgs.dayTypeInvite = "Giorno";
   msgs.monthTypeInvite = "Mese";
   msgs.yearTypeInvite = "Anno";
   msgs.cancelEditor = "Annulla";
   msgs.okEditor = "Ok";
   msgs.defautCalendarOpts = {
      navigator: {
        strings : {
            month: "Seleziona un mese",
            year: "Digita un anno",
            submit: "Ok",
            cancel: "Annulla",
            invalidYear: "Anno non valido"
         }
      },
      start_weekday: 1 // la semaine commence un lundi
   };

   // Datatable
   msgs.saveText = "Salva";
   msgs.cancelText = "Annulla";
   msgs.modifyText = "Modifica";
   msgs.deleteText = "Elimina";
   msgs.insertItemText = "Aggiungi";
   msgs.confirmDeletion = "Sei sicuro?";

	// for YUI loader 
   inputEx.lang_it = true;

})();