/* report controls */
function hide_report_controls() {
   $('#report_controls').hide();
   $('#report_controls_show').show();
   document.form1.show_controls.value = 0;
   return true;
}
function show_report_controls() {
   $('#report_controls').show();
   $('#report_controls_show').hide();
   document.form1.show_controls.value = 1;
   return true;
}

/* column chooser */
function hide_column_chooser() {
   $('#column_chooser').hide();
   $('#column_chooser_show').show();
   document.form1.show_chooser.value = 0;
   return true;
}
function show_column_chooser() {
   $('#column_chooser').show();
   $('#column_chooser_show').hide();
   document.form1.show_chooser.value = 1;
   return true;
}
function clear_controls() {
    document.form1.clear_cntrls.value = 1;
    document.form1.submit();
    return true;
}
function reset_column_defaults() {
    $('#choose_columns,:checkbox').prop('checked', false);
    $('#choose_columns,.default_column').prop('checked', true);
    document.form1.submit();
    return true;
}
/*function select_all_columns() {
    $('#choose_columns,:checkbox').prop('checked', true);
    document.form1.submit();
    return true;
}*/

/* sql panel */
function hide_sql_panel() {
   $('#sql_panel').hide();
   $('#sql_panel_show').show();
   document.form1.show_sql_panel.value = 0;
   return true;
}
function show_sql_panel() {
   $('#sql_panel').show();
   $('#sql_panel_show').hide();
   document.form1.show_sql_panel.value = 1;
   return true;
}

/* paging controls */
function go_to_prev_page() {
    document.form1.page_num.value = parseInt(document.form1.page_num.value)-1;
    document.form1.submit(); 
    return true;
}
function go_to_next_page() {
    document.form1.page_num.value = parseInt(document.form1.page_num.value)+1;
    document.form1.submit(); 
    return true;
}

/* sort controls */
function set_sort(column_name, direction) {
    document.form1.sort_by.value = column_name + ':' + direction
    document.form1.submit();
    return true;
}
function set_s_sort(column_name, direction) {
    document.form1.s_sort_by.value = column_name + ':' + direction
    document.form1.submit();
    return true;
}

function dateDifferenceInDays(dateStr) {
  var splitDate = dateStr.split('-');
  var then = new Date(parseInt(splitDate[0]), parseInt(splitDate[1] - 1), parseInt(splitDate[2]));
  var now = new Date();
  var differenceInDays = Math.floor((now - then) / 86400000.0);
  return differenceInDays;
}

function dateDifferenceInMonths(dateStr) {
  // This is not a general purpose function. It assumes the day of month in dateStr is
  // the same as the current day of month, and that dateStr is in the past.
  // Do not call this otherwise.
  var splitDate = dateStr.split('-');
  var now = new Date();
  var months = 0;
  
  months += (now.getFullYear() - parseInt(splitDate[0])) * 12;
  months += (now.getMonth() + 1) - parseInt(splitDate[1]);

  return months;
}

function relativeDateAsString(date) {
  var interpretations = [];
  var daysAgo = dateDifferenceInDays(date);
  var year = parseInt(date.substring(0, 4));
  var month = parseInt(date.substring(5, 7));
  var day = parseInt(date.substring(8, 10));
  var today = new Date();

  interpretations.push({string : "Keep '" + date + "'",
                        code   : date});

  if(daysAgo == 0) {
    interpretations.push({string : "Use 'Today'",
                          code   : "#DAYSAGO:0"});
  } else if(daysAgo == 1) {
    interpretations.push({string : "Use 'Yesterday'",
                          code   : "#DAYSAGO:1"});
  } else {
    interpretations.push({string : "Use '" + daysAgo + " Days Ago'",
                          code   : "#DAYSAGO:" + daysAgo});
  }

  if(year == today.getFullYear() && month == today.getMonth() + 1 && day == 1) {
    interpretations.push({string : "Use 'Current Month'",
                          code   : "#CURRENT:MONTH"});
  }
  if(year == today.getFullYear() && month == 1 && day == 1) {
    interpretations.push({string : "Use 'Current Year'",
                          code   : "#CURRENT:YEAR"});
  }
  if(year == today.getFullYear() && month == today.getMonth() && day == today.getDate()) {
    interpretations.push({string : "Use 'One Month Ago'",
                          code   : "#MONTHSAGO:1"});
  } else if(day == today.getDate()) {
    var monthsAgo = dateDifferenceInMonths(date);
    if(monthsAgo % 12 != 0) { // Don't provide equivalent statements like "12 Months Ago" and "One Year Ago"
      interpretations.push({string : "Use '" + monthsAgo + " Months Ago'",
                            code   : "#MONTHSAGO:" + monthsAgo});
    }
  }
  if(year == today.getFullYear() - 1 && month == today.getMonth() && day == today.getDate()) {
    interpretations.push({string : "Use 'One Year Ago'",
                          code   : "#YEARSAGO:1"});
  }

  return interpretations;
}

/* save controls */
function save_report() {
  $("#save-panel #questions").text("");
  $(".date").each(function() {
    var date = $(this).val();
    if(date != "") {
      var interpretations = relativeDateAsString(date);
      var fieldLabel = $(this).closest("tr").find("td:first-child").text();
      var fieldName = $(this).attr('name');
      $("#save-panel #questions").append(function() {
        var str = "<div class='question'>In the '" + fieldLabel + "' field, you wrote '" + date + "'. Did you want this exact date, or do you want it change relative to the current date?<br>";
        var idx = 0;
        str += "<div class='form-section'>";
        interpretations.forEach(function(interpretation) {
          idx += 1;
          str += "<input type='radio' name='" + fieldName + "_newvalue' value='" + interpretation.code + "' id='" + fieldName + idx + "'>" +
                 "<label for='" + fieldName + idx + "'>" + interpretation.string + "</label><br>";
        });
        str += "</div></div>";
        return str;
      });
    }
  });

  $("#save-panel").show();

  var url = document.URL;
  if(url.indexOf('#') == -1) {
    var pageName = url.substring(url.lastIndexOf("/") + 1, url.length - 3);
  } else {
    var pageName = url.substring(url.lastIndexOf("/") + 1, url.length - 4);
  }
  if($("#save-panel input[name=report_title]").val() == "") {
    $("#save-panel input[name=report_title]").val(pageName);
  }
  $("#save-panel input[type=button]").on('click', function() {
    $.ajax({
      method: 'POST',
      data: $('form[name=form1]').serialize(),
      url: "/custom_report.py"
    }).done(function() {
      window.location.href = "/main.py";
    });
  });
}

$(function() {
   $(".date").datepicker({dateFormat: "yy-mm-dd" });

   if (document.form1.show_controls.value == 1) {
      $("#report_controls_show").hide();
   } else {
     $("#report_controls").hide()
   }

   if (document.form1.show_chooser.value == 1) {
      $("#column_chooser_show").hide();
   } else {
     $("#column_chooser").hide()
   }

   if (document.form1.show_sql.value == 1) {
      $("#sql_panel_show").hide();
   } else {
     $("#sql_panel").hide()
   }

   // Fix form action if current page contains GET parameters
   if(window.location.href.indexOf('?') != -1) {
     var cleanUrl = window.location.href.substring(0, window.location.href.indexOf('?'));
     $("form[name=form1]")
       .attr('action', cleanUrl)
       .attr('method', 'POST');
   }

   $("#save-panel .cancel").on('click', function() {
     $("#save-panel").hide();
   });
});
