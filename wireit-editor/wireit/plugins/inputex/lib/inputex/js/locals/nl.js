// Dutch translations for inputEx 0.2.2. Courtesy of Oqapi (http://www.oqapi.nl).
(function () {

   var msgs = inputEx.messages;

   msgs.required = "Dit veld is verplicht";
   msgs.invalid = "Dit veld is incorrect";
   msgs.valid = "Dit veld is correct";
   msgs.invalidEmail = "Het emailadres is incorrect; bv. example@test.com";
   msgs.selectColor = "Kies een kleur :";
   msgs.invalidPassword = ["Het paswoord moet bestaan uit minstens "," karakters (letters of cijfers)."];
   msgs.invalidPasswordConfirmation = "De ingevoerde paswoorden komen niet overeen!";
   msgs.capslockWarning = "Let op: de caps-lock staat aan.";
   msgs.invalidDate = "De datum is incorrect; bv: 25/01/2007";
   msgs.defaultDateFormat = "d/m/Y";
   msgs.shortMonths = ["Jan", "Feb", "Mrt", "Apr", "Mei", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
   msgs.months = ["Januari", "Februari", "Maart", "April", "Mei", "Juni", "Juli", "Augustus", "September", "Oktober", "November", "December"];
   msgs.weekdays1char =  ["Z", "M", "D", "W", "D", "V", "Z"];
   msgs.shortWeekdays = ["Zo","Ma","Di","Wo","Do","Vr","Za"];
   msgs.selectMonth = "- Maak een keuze -";
   msgs.dayTypeInvite = "Dag";
   msgs.monthTypeInvite = "Maand";
   msgs.yearTypeInvite = "Jaar";
   msgs.cancelEditor = "annuleren";
   msgs.okEditor = "Ok";
   msgs.defautCalendarOpts = {
      navigator: {
               strings : {
                   month: "Kies een maand",
                   year: "Voer een jaar in",
                   submit: "Ok",
                   cancel: "Annuleren",
                   invalidYear: "Jaar is incorrect"
               }
      },
      start_weekday: 0
   };


   // Datatable
   msgs.saveText = "Opslaan";
   msgs.cancelText = "Annuleren";
   msgs.modifyText = "Wijzigen";
   msgs.deleteText = "Verwijderen";
   msgs.insertItemText = "Toevoegen";
   msgs.confirmDeletion = "Weet u het zeker?";

   msgs.stringTooShort = ["Dit veld moet tenminste "," nummers of karakters bevatten"];
   msgs.stringTooLong  = ["Dit veld mag maximaal "," nummers of karakters bevatten"];

   msgs.invalidUrl = "Ongeldige URL, bv: http://www.test.com";

	// for YUI loader 
   inputEx.lang_nl = true;

})();