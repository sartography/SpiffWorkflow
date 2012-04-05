// InputEx Spanish localization
(function() {

   var msgs = inputEx.messages;

   msgs.required = "Este campo es obligatorio";
   msgs.invalid = "Este campo no es válido";
   msgs.valid = "Este campo es válido";
   
   msgs.invalidEmail = "Email no válido; ej: tu.nombre@correo.es";
   msgs.selectColor = "Selecciona un color:";
   msgs.invalidPassword = ["La password debe contener al menos ","numeros o letras"];
   msgs.invalidPasswordConfirmation = "las password son diferentes !";
   msgs.passwordStrength = "La password es demasiado debil";
   msgs.capslockWarning = "Atencione: bloqueo de mayúsculas activado";
   msgs.invalidDate = "Fecha no válida; ej: 25/01/2007";
   msgs.defaultDateFormat = "d/m/Y";
   msgs.shortMonths=["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
   msgs.months=["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];
   msgs.weekdays1char=["D", "L", "M", "X", "J", "V", "S"];
   msgs.shortWeekdays=["Do", "Lu", "Ma", "Mi", "Ju", "Vi", "Sa"];
   msgs.selectMonth = "- Selccione Mes -";
   msgs.dayTypeInvite = "Día";
   msgs.monthTypeInvite = "Mes";
   msgs.yearTypeInvite = "Año";
   msgs.cancelEditor = "Cancelar";
   msgs.okEditor = "Aceptar";
   msgs.defautCalendarOpts = {
      navigator: {
        strings : {
            month: "Seleccione mes",
            year: "Introduzca año",
            submit: "Aceptar",
            cancel: "Cancelar",
            invalidYear: "Año no válido"
         }
      },
      start_weekday: 1 // la semaine commence un lundi
   };
   msgs.stringTooShort = ["Este campo debe contener al menos "," caracteres (letras o números)"];
   msgs.stringTooLong = ["Este campo debe contener como mucho "," caracteres (letras o números)"];
   msgs.ajaxWait = "Enviando...";
   msgs.menuTypeInvite = "Haga click aquí para seleccionar";
   
   // List
   msgs.listAddLink = "Añadir";
   msgs.listRemoveLink = "Eliminar";
   

   // Datatable
   msgs.saveText = "Salvar";
   msgs.cancelText = "Cancelar";
   msgs.modifyText = "Modificar";
   msgs.deleteText = "Eliminar";
   msgs.insertItemText = "Insertar";
   msgs.confirmDeletion = "¿Está seguro que desea borrar?";
   
      
   // TimeInterval
   msgs.timeUnits = {
      SECOND: "segundos",
      MINUTE: "minutos",
      HOUR: "horas",
      DAY: "días",
      MONTH: "meses",
      YEAR: "años"
   };
   
   // for YUI loader 
   inputEx.lang_es = true;
})();